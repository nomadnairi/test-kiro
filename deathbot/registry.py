"""Tool registry — the single source of truth for the button UI.

Every capability the bot exposes is declared here once. The menu keyboards and
the input dispatcher are generated from this list, so adding a tool means adding
one entry — no new handler, no new command.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import escape, unescape
from typing import TYPE_CHECKING, Awaitable, Callable

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Turn the HTML we send to Telegram back into plain text for file exports."""
    return unescape(_TAG_RE.sub("", text))

if TYPE_CHECKING:
    from .container import Container

# Category id -> button label (order defines the main-menu layout).
CATEGORIES: list[tuple[str, str]] = [
    ("osint", "🔎 OSINT"),
    ("pentest", "🛠 Pentest"),
    ("ai", "🤖 AI"),
    ("agents", "🧠 Agents"),
    ("productivity", "📝 Notes & Todo"),
    ("export", "📤 Export"),
    ("settings", "⚙️ Settings"),
    ("admin", "🛡 Admin"),
]


@dataclass(slots=True)
class Result:
    text: str
    filename: str | None = None
    file_bytes: bytes | None = None


@dataclass(slots=True)
class Tool:
    id: str
    label: str
    category: str
    module: str                       # access scope checked before running
    kind: str = "input"               # input | instant | chat | photo | apikey
    prompt: str | None = None
    run: Callable[["Container", int, str], Awaitable[Result]] | None = None


# --------------------------------------------------------------------------- #
# formatting helpers
# --------------------------------------------------------------------------- #
def _pre(text: str, limit: int = 3200) -> str:
    text = text if len(text) <= limit else text[:limit] + "\n… (truncated)"
    return f"<pre>{escape(text)}</pre>"


def human(title: str, data: dict) -> str:
    """Render a result dict into readable Telegram HTML."""
    lines = [f"<b>{escape(title)}</b>"]
    raw_keys = ("raw", "output", "note", "hint", "reason")
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        if key in raw_keys:
            lines.append(_pre(str(value)))
        elif isinstance(value, dict):
            inner = "\n".join(f"  {escape(str(k))}: {escape(str(v))}"
                              for k, v in value.items() if v not in (None, ""))
            lines.append(f"<b>{escape(key)}</b>:\n{inner}")
        elif isinstance(value, list):
            if not value:
                continue
            if isinstance(value[0], dict):
                items = "\n".join("  • " + ", ".join(f"{k}={v}" for k, v in d.items())
                                  for d in value[:25])
            else:
                items = "\n".join(f"  • {escape(str(v))}" for v in value[:40])
            more = f"\n  … +{len(value) - 40} more" if len(value) > 40 else ""
            lines.append(f"<b>{escape(key)}</b> ({len(value)}):\n{items}{more}")
        else:
            lines.append(f"<b>{escape(key)}</b>: {escape(str(value))}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# run() implementations
# --------------------------------------------------------------------------- #
def _osint(method: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        data = await getattr(c.osint, method)(uid, arg)
        return Result(human(f"{title}: {arg}", data))
    return _run


def _pentest_native(method: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        data = await getattr(c.pentest, method)(uid, arg)
        return Result(human(f"{title}: {arg}", data))
    return _run


def _external(tool_id: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        data = await c.pentest.external(uid, tool_id, arg)
        return Result(human(f"{title}: {arg}", data))
    return _run


def _agent(agent_id: str, title: str):
    async def _run(c: "Container", uid: int, arg: str) -> Result:
        agent = c.agents[agent_id]
        answer = await agent.run(arg)
        await c.repos.audit.log(uid, f"agent.{agent_id}", arg[:60])
        return Result(f"<b>{escape(title)}</b>\n\n{escape(answer)}")
    return _run


async def _ai_ask(c: "Container", uid: int, arg: str) -> Result:
    return Result(escape(await c.ai.ask(uid, arg)))


async def _ai_reset(c: "Container", uid: int, _: str) -> Result:
    await c.ai.reset(uid)
    return Result("🧹 Conversation history cleared.")


async def _ai_providers(c: "Container", uid: int, _: str) -> Result:
    avail = c.ai.available_providers()
    return Result("<b>AI providers</b>\nAvailable: " + (", ".join(avail) or "none — add a key in ⚙️ Settings"))


async def _note_add(c: "Container", uid: int, arg: str) -> Result:
    nid = await c.notes.add(uid, arg)
    return Result(f"📝 Saved note #{nid}")


async def _note_list(c: "Container", uid: int, _: str) -> Result:
    notes = await c.notes.list(uid)
    if not notes:
        return Result("No notes yet.")
    return Result("<b>Your notes</b>\n" + "\n".join(
        f"#{n['id']} {escape(n['title'] or 'untitled')}" for n in notes))


async def _todo_add(c: "Container", uid: int, arg: str) -> Result:
    tid = await c.todos.add(uid, arg)
    return Result(f"✅ Added todo #{tid}")


async def _todo_list(c: "Container", uid: int, _: str) -> Result:
    todos = await c.todos.list(uid)
    if not todos:
        return Result("No todos yet.")
    return Result("<b>Your todos</b>\n" + "\n".join(
        f"{'☑️' if t['done'] else '⬜'} #{t['id']} {escape(t['text'])}" for t in todos))


async def _todo_done(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Send a numeric todo id.")
    ok = await c.todos.done(uid, int(arg.strip()))
    return Result("☑️ Completed." if ok else "Not found.")


async def _profile(c: "Container", uid: int, _: str) -> Result:
    p = await c.users.profile(uid)
    if not p:
        return Result("No profile yet.")
    return Result(human("Your profile", {
        "id": p["id"], "username": p["username"], "role": p["role"],
        "notes": p["notes"], "todos": p["todos"],
        "AI keys": ", ".join(p["providers"]) or "—", "since": p["created_at"],
    }))


async def _keys_list(c: "Container", uid: int, _: str) -> Result:
    provs = await c.api_keys.list_providers(uid)
    return Result("🔑 Stored keys: " + (", ".join(provs) or "none"))


async def _set_provider(c: "Container", uid: int, arg: str) -> Result:
    await c.settings_svc.set(uid, "ai_provider", arg.strip().lower())
    return Result(f"✅ Default AI provider set to {escape(arg.strip().lower())}")


async def load_last_report(c: "Container", uid: int) -> dict | None:
    raw = await c.repos.cache.get(f"report:{uid}")
    return json.loads(raw) if raw else None


async def save_last_report(c: "Container", uid: int, report: dict) -> None:
    await c.repos.cache.set(f"report:{uid}", json.dumps(report), ttl_seconds=86400)


async def build_export(c: "Container", uid: int, fmt: str) -> Result:
    """Render the user's last tool result (or their notes/todos) into a file."""
    report = await load_last_report(c, uid)
    if report is None:
        notes = await c.notes.list(uid)
        todos = await c.todos.list(uid)
        report = c.report.build("DeathBot workspace", {
            "notes": "\n".join(f"- {n['title']}: {n['body']}" for n in notes) or "none",
            "todos": "\n".join(f"[{'x' if t['done'] else ' '}] {t['text']}" for t in todos) or "none",
        })
        report["tags"] = ["deathbot", "workspace"]
    blob = c.export.render(report, fmt)
    ext = c.export.extension(fmt)
    safe = re.sub(r"[^a-z0-9]+", "-", report["title"].lower()).strip("-")[:40] or "report"
    return Result(f"📤 <b>{escape(report['title'])}</b> → {fmt.upper()}",
                  filename=f"{safe}.{ext}", file_bytes=blob)


def _export(fmt: str):
    async def _run(c: "Container", uid: int, _: str) -> Result:
        return await build_export(c, uid, fmt)
    return _run


async def _users(c: "Container", uid: int, _: str) -> Result:
    users = await c.users.list_users(30)
    return Result("<b>Users</b>\n" + "\n".join(
        f"<code>{u['id']}</code> @{u['username'] or '—'} — {u['role']}"
        + (" 🚫" if u["is_banned"] else "") for u in users))


async def _grant(c: "Container", uid: int, arg: str) -> Result:
    parts = arg.split()
    from .core.roles import ROLE_ORDER
    if len(parts) != 2 or not parts[0].isdigit() or parts[1] not in ROLE_ORDER:
        return Result(f"Format: <code>&lt;user_id&gt; &lt;role&gt;</code>\nRoles: {', '.join(ROLE_ORDER)}")
    await c.access.grant(uid, int(parts[0]), parts[1])
    return Result(f"✅ {parts[0]} → {parts[1]}")


async def _ban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Send a numeric user id.")
    await c.access.ban(uid, int(arg.strip()), True)
    return Result("🚫 Banned.")


async def _unban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Send a numeric user id.")
    await c.access.ban(uid, int(arg.strip()), False)
    return Result("✅ Unbanned.")


async def _audit(c: "Container", uid: int, _: str) -> Result:
    rows = await c.repos.audit.recent(25)
    if not rows:
        return Result("No audit entries.")
    return Result("<b>Recent audit</b>\n" + "\n".join(
        f"{r['created_at']} · {r['user_id']} · {r['action']} {r['detail'] or ''}" for r in rows))


# --------------------------------------------------------------------------- #
# the registry
# --------------------------------------------------------------------------- #
def _t(**kw) -> Tool:
    return Tool(**kw)

TOOLS: dict[str, Tool] = {t.id: t for t in [
    # ---- OSINT ----
    _t(id="whois", label="WHOIS", category="osint", module="osint",
       prompt="Send a domain (e.g. example.com)", run=_osint("whois", "WHOIS")),
    _t(id="dns", label="DNS", category="osint", module="osint",
       prompt="Send a host/domain", run=_osint("dns", "DNS")),
    _t(id="subdomains", label="Subdomains", category="osint", module="osint",
       prompt="Send a domain (crt.sh)", run=_osint("subdomains", "Subdomains")),
    _t(id="username", label="Username", category="osint", module="osint",
       prompt="Send a username to search across sites", run=_osint("username", "Username")),
    _t(id="email", label="Email", category="osint", module="osint",
       prompt="Send an email address", run=_osint("email", "Email")),
    _t(id="phone", label="Phone", category="osint", module="osint",
       prompt="Send a phone number (+countrycode…)", run=_osint("phone", "Phone")),
    _t(id="geoip", label="GeoIP", category="osint", module="geoint",
       prompt="Send an IP or host", run=_osint("geoip", "GeoIP")),
    _t(id="shodan", label="Shodan", category="osint", module="osint",
       prompt="Send an IP (needs Shodan key)", run=_osint("shodan", "Shodan")),
    _t(id="threatintel", label="Threat Intel", category="osint", module="osint",
       prompt="Send an IP / domain / URL", run=_osint("threat_intel", "Threat Intel")),
    _t(id="ioc", label="IOC", category="osint", module="osint",
       prompt="Send an indicator (IP/hash/CVE/domain…)", run=_osint("ioc", "IOC")),
    _t(id="revimg", label="Reverse Image", category="osint", module="image",
       prompt="Send an image URL", run=_osint("reverse_image", "Reverse Image")),
    _t(id="exif", label="Metadata/EXIF", category="osint", module="image",
       kind="photo", prompt="Send a photo (as file for full EXIF)"),
    _t(id="darknet", label="Darknet", category="osint", module="osint",
       prompt="Send a query", run=_osint("darknet", "Darknet")),

    # ---- Pentest ----
    _t(id="portscan", label="Port Scan", category="pentest", module="recon",
       prompt="Send a host (authorised only)", run=_pentest_native("scan_ports", "Port Scan")),
    _t(id="sslscan", label="SSL Scan", category="pentest", module="recon",
       prompt="Send a host", run=_pentest_native("ssl_scan", "SSL Scan")),
    _t(id="techdetect", label="Tech Detect", category="pentest", module="web",
       prompt="Send a URL", run=_pentest_native("tech_detect", "Tech Detect")),
    _t(id="subfinder", label="subfinder", category="pentest", module="recon",
       prompt="Send a domain", run=_external("subfinder", "subfinder")),
    _t(id="amass", label="amass", category="pentest", module="recon",
       prompt="Send a domain", run=_external("amass", "amass")),
    _t(id="httpx", label="httpx", category="pentest", module="recon",
       prompt="Send a URL/host", run=_external("httpx", "httpx")),
    _t(id="naabu", label="naabu", category="pentest", module="recon",
       prompt="Send a host", run=_external("naabu", "naabu")),
    _t(id="nuclei", label="nuclei", category="pentest", module="recon",
       prompt="Send a URL (authorised only)", run=_external("nuclei", "nuclei")),
    _t(id="katana", label="katana", category="pentest", module="recon",
       prompt="Send a URL", run=_external("katana", "katana")),
    _t(id="masscan", label="masscan", category="pentest", module="recon",
       prompt="Send a host/CIDR (authorised only)", run=_external("masscan", "masscan")),
    _t(id="rustscan", label="rustscan", category="pentest", module="recon",
       prompt="Send a host", run=_external("rustscan", "rustscan")),
    _t(id="gobuster", label="gobuster", category="pentest", module="recon",
       prompt="Send a domain", run=_external("gobuster", "gobuster")),
    _t(id="ffuf", label="ffuf", category="pentest", module="web",
       prompt="Send a URL with FUZZ", run=_external("ffuf", "ffuf")),
    _t(id="ferox", label="feroxbuster", category="pentest", module="web",
       prompt="Send a URL", run=_external("feroxbuster", "feroxbuster")),

    # ---- AI ----
    _t(id="ai_ask", label="Ask AI", category="ai", module="ai",
       prompt="Send your question", run=_ai_ask),
    _t(id="ai_chat", label="Chat mode", category="ai", module="ai", kind="chat"),
    _t(id="ai_providers", label="Providers", category="ai", module="ai",
       kind="instant", run=_ai_providers),
    _t(id="ai_reset", label="Reset history", category="ai", module="ai",
       kind="instant", run=_ai_reset),

    # ---- Agents ----
    _t(id="ag_general", label="General", category="agents", module="ai",
       prompt="Describe the task", run=_agent("general", "General Assistant")),
    _t(id="ag_osint", label="OSINT", category="agents", module="ai",
       prompt="Describe the target", run=_agent("osint", "OSINT Agent")),
    _t(id="ag_recon", label="Recon", category="agents", module="ai",
       prompt="Describe the target", run=_agent("recon", "Recon Agent")),
    _t(id="ag_report", label="Report", category="agents", module="ai",
       prompt="Paste findings to summarise", run=_agent("report", "Report Agent")),
    _t(id="ag_threat", label="Threat Intel", category="agents", module="ai",
       prompt="Send indicators", run=_agent("threatintel", "Threat Intel Agent")),
    _t(id="ag_code", label="Code", category="agents", module="ai",
       prompt="Describe the code task", run=_agent("code", "Code Agent")),
    _t(id="ag_research", label="Research", category="agents", module="ai",
       prompt="Send a research question", run=_agent("research", "Research Agent")),
    _t(id="ag_planner", label="Planner", category="agents", module="ai",
       prompt="Send an objective", run=_agent("planner", "Planner Agent")),

    # ---- Productivity ----
    _t(id="note_add", label="➕ Note", category="productivity", module="notes",
       prompt="Send note text (first line = title)", run=_note_add),
    _t(id="note_list", label="📋 Notes", category="productivity", module="notes",
       kind="instant", run=_note_list),
    _t(id="todo_add", label="➕ Todo", category="productivity", module="todo",
       prompt="Send todo text", run=_todo_add),
    _t(id="todo_list", label="📋 Todos", category="productivity", module="todo",
       kind="instant", run=_todo_list),
    _t(id="todo_done", label="☑️ Done", category="productivity", module="todo",
       prompt="Send a todo id to complete", run=_todo_done),

    # ---- Export ----
    _t(id="exp_pdf", label="PDF", category="export", module="reports", kind="instant", run=_export("pdf")),
    _t(id="exp_docx", label="DOCX", category="export", module="reports", kind="instant", run=_export("docx")),
    _t(id="exp_html", label="HTML", category="export", module="reports", kind="instant", run=_export("html")),
    _t(id="exp_md", label="Markdown", category="export", module="reports", kind="instant", run=_export("markdown")),
    _t(id="exp_csv", label="CSV", category="export", module="reports", kind="instant", run=_export("csv")),
    _t(id="exp_json", label="JSON", category="export", module="reports", kind="instant", run=_export("json")),

    # ---- Settings ----
    _t(id="profile", label="👤 Profile", category="settings", module="profile",
       kind="instant", run=_profile),
    _t(id="keys", label="🔑 Keys", category="settings", module="profile",
       kind="instant", run=_keys_list),
    _t(id="addkey", label="➕ Add key", category="settings", module="profile", kind="apikey"),
    _t(id="setprov", label="Set provider", category="settings", module="profile",
       prompt="Send a provider name (openrouter, openai, claude, gemini…)", run=_set_provider),

    # ---- Admin ----
    _t(id="users", label="Users", category="admin", module="admin", kind="instant", run=_users),
    _t(id="grant", label="Grant", category="admin", module="admin",
       prompt="Send: <user_id> <role>", run=_grant),
    _t(id="ban", label="Ban", category="admin", module="admin",
       prompt="Send a user id to ban", run=_ban),
    _t(id="unban", label="Unban", category="admin", module="admin",
       prompt="Send a user id to unban", run=_unban),
    _t(id="audit", label="Audit log", category="admin", module="audit",
       kind="instant", run=_audit),
]}


def tools_in(category: str) -> list[Tool]:
    return [t for t in TOOLS.values() if t.category == category]


def get_tool(tool_id: str) -> Tool | None:
    return TOOLS.get(tool_id)
