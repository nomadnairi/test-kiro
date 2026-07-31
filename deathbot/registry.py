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


_TRANSLIT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
})


def _slug(title: str) -> str:
    """Filesystem-safe file stem — titles are Russian, so transliterate first."""
    stem = re.sub(r"[^a-z0-9]+", "-", title.lower().translate(_TRANSLIT))
    return stem.strip("-")[:40] or "report"

if TYPE_CHECKING:
    from .container import Container

# Category id -> button label (order defines the main-menu layout).
CATEGORIES: list[tuple[str, str]] = [
    ("osint", "🔎 OSINT"),
    ("pentest", "🛠 Пентест"),
    ("ai", "🤖 ИИ"),
    ("agents", "🧠 Агенты"),
    ("productivity", "📝 Заметки и задачи"),
    ("export", "📤 Экспорт"),
    ("settings", "⚙️ Настройки"),
    ("admin", "🛡 Админ"),
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
    text = text if len(text) <= limit else text[:limit] + "\n… (обрезано)"
    return f"<pre>{escape(text)}</pre>"


# Field names come back from the tool modules in English; show them in Russian.
FIELD_LABELS: dict[str, str] = {
    "domain": "домен", "host": "хост", "query": "запрос", "url": "ссылка",
    "addresses": "адреса", "reverse": "обратная запись", "error": "ошибка",
    "subdomains": "поддомены", "count": "найдено", "checked": "проверено",
    "username": "юзернейм", "found": "найдено", "found_count": "найдено профилей",
    "email": "email", "valid_format": "формат верный", "gravatar": "gravatar",
    "hibp": "утечки (HIBP)", "breaches": "утечки", "available": "доступно",
    "input": "ввод", "digits": "цифры", "e164": "формат E.164",
    "country_guess": "страна (предположительно)", "length": "длина",
    "country": "страна", "regionName": "регион", "city": "город", "zip": "индекс",
    "lat": "широта", "lon": "долгота", "isp": "провайдер", "org": "организация",
    "as": "AS", "timezone": "часовой пояс", "map": "карта",
    "ports": "порты", "open_ports": "открытые порты", "hostnames": "имена хостов",
    "vulns": "уязвимости", "os": "ОС", "engine": "движок",
    "indicator": "индикатор", "sources": "источники", "listed": "в списках",
    "url_count": "ссылок", "urls": "ссылки", "abuse_score": "уровень угрозы",
    "total_reports": "всего жалоб", "source": "источник",
    "value": "значение", "type": "тип", "suggested_lookups": "что ещё проверить",
    "image_url": "ссылка на изображение", "engines": "поисковики",
    "format": "формат", "size": "размер", "camera": "камера",
    "datetime": "дата съёмки", "software": "софт", "gps": "GPS",
    "tool": "инструмент", "target": "цель", "installed": "установлен",
    "ok": "успешно", "output": "вывод", "raw": "ответ", "note": "примечание",
    "hint": "подсказка", "reason": "причина", "status": "статус",
    "tls_version": "версия TLS", "cipher": "шифр", "subject_cn": "выдан на",
    "issuer": "издатель", "valid_from": "действует с", "valid_until": "действует до",
    "days_until_expiry": "дней до истечения", "san": "альт. имена",
    "server": "сервер", "powered_by": "работает на", "frameworks": "фреймворки",
    "headers_of_interest": "заголовки", "security_headers": "заголовки безопасности",
    "port": "порт", "profiles": "профили", "sites": "сайты",
    "unavailable": "занято", "availableCount": "свободно", "unavailableCount": "занято",
    "id": "ID", "role": "роль", "notes": "заметки", "todos": "задачи",
    "since": "с", "pending_update_count": "апдейтов в очереди",
}


def _label(key: str) -> str:
    return FIELD_LABELS.get(key, key)


def human(title: str, data: dict) -> str:
    """Render a result dict into readable Telegram HTML."""
    lines = [f"<b>{escape(title)}</b>"]
    raw_keys = ("raw", "output", "note", "hint", "reason")
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        name = _label(key)
        if key in raw_keys:
            lines.append(_pre(str(value)))
        elif isinstance(value, dict):
            inner = "\n".join(f"  {escape(_label(str(k)))}: {escape(str(v))}"
                              for k, v in value.items() if v not in (None, ""))
            lines.append(f"<b>{escape(name)}</b>:\n{inner}")
        elif isinstance(value, list):
            if not value:
                continue
            if isinstance(value[0], dict):
                items = "\n".join("  • " + ", ".join(f"{_label(k)}={v}" for k, v in d.items())
                                  for d in value[:25])
            else:
                items = "\n".join(f"  • {escape(str(v))}" for v in value[:40])
            more = f"\n  … ещё {len(value) - 40}" if len(value) > 40 else ""
            lines.append(f"<b>{escape(name)}</b> ({len(value)}):\n{items}{more}")
        else:
            lines.append(f"<b>{escape(name)}</b>: {escape(str(value))}")
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
    return Result("🧹 История диалога очищена.")


async def _ai_providers(c: "Container", uid: int, _: str) -> Result:
    avail = c.ai.available_providers()
    return Result("<b>ИИ-провайдеры</b>\nДоступны: "
                  + (", ".join(avail) or "нет — добавь ключ в ⚙️ Настройках"))


async def _note_add(c: "Container", uid: int, arg: str) -> Result:
    nid = await c.notes.add(uid, arg)
    return Result(f"📝 Заметка #{nid} сохранена")


async def _note_list(c: "Container", uid: int, _: str) -> Result:
    notes = await c.notes.list(uid)
    if not notes:
        return Result("Заметок пока нет.")
    return Result("<b>Твои заметки</b>\n" + "\n".join(
        f"#{n['id']} {escape(n['title'] or 'без названия')}" for n in notes))


async def _todo_add(c: "Container", uid: int, arg: str) -> Result:
    tid = await c.todos.add(uid, arg)
    return Result(f"✅ Задача #{tid} добавлена")


async def _todo_list(c: "Container", uid: int, _: str) -> Result:
    todos = await c.todos.list(uid)
    if not todos:
        return Result("Задач пока нет.")
    return Result("<b>Твои задачи</b>\n" + "\n".join(
        f"{'☑️' if t['done'] else '⬜'} #{t['id']} {escape(t['text'])}" for t in todos))


async def _todo_done(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь номер задачи (число).")
    ok = await c.todos.done(uid, int(arg.strip()))
    return Result("☑️ Выполнено." if ok else "Не найдено.")


async def _profile(c: "Container", uid: int, _: str) -> Result:
    p = await c.users.profile(uid)
    if not p:
        return Result("Профиля пока нет.")
    return Result(human("Твой профиль", {
        "id": p["id"], "username": p["username"], "role": p["role"],
        "notes": p["notes"], "todos": p["todos"],
        "ключи ИИ": ", ".join(p["providers"]) or "—", "since": p["created_at"],
    }))


async def _keys_list(c: "Container", uid: int, _: str) -> Result:
    provs = await c.api_keys.list_providers(uid)
    return Result("🔑 Сохранённые ключи: " + (", ".join(provs) or "нет"))


async def _set_provider(c: "Container", uid: int, arg: str) -> Result:
    await c.settings_svc.set(uid, "ai_provider", arg.strip().lower())
    return Result(f"✅ Провайдер ИИ по умолчанию: {escape(arg.strip().lower())}")


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
        report = c.report.build("Рабочее пространство DeathBot", {
            "Заметки": "\n".join(f"- {n['title']}: {n['body']}" for n in notes) or "нет",
            "Задачи": "\n".join(f"[{'x' if t['done'] else ' '}] {t['text']}" for t in todos) or "нет",
        })
        report["tags"] = ["deathbot", "workspace"]
    blob = c.export.render(report, fmt)
    ext = c.export.extension(fmt)
    safe = _slug(report["title"])
    return Result(f"📤 <b>{escape(report['title'])}</b> → {fmt.upper()}",
                  filename=f"{safe}.{ext}", file_bytes=blob)


def _export(fmt: str):
    async def _run(c: "Container", uid: int, _: str) -> Result:
        return await build_export(c, uid, fmt)
    return _run


async def _users(c: "Container", uid: int, _: str) -> Result:
    users = await c.users.list_users(30)
    return Result("<b>Пользователи</b>\n" + "\n".join(
        f"<code>{u['id']}</code> @{u['username'] or '—'} — {u['role']}"
        + (" 🚫" if u["is_banned"] else "") for u in users))


async def _grant(c: "Container", uid: int, arg: str) -> Result:
    parts = arg.split()
    from .core.roles import ROLE_ORDER
    if len(parts) != 2 or not parts[0].isdigit() or parts[1] not in ROLE_ORDER:
        return Result("Формат: <code>&lt;id пользователя&gt; &lt;роль&gt;</code>\n"
                      f"Роли: {', '.join(ROLE_ORDER)}")
    await c.access.grant(uid, int(parts[0]), parts[1])
    return Result(f"✅ {parts[0]} → {parts[1]}")


async def _ban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь ID пользователя (число).")
    await c.access.ban(uid, int(arg.strip()), True)
    return Result("🚫 Забанен.")


async def _unban(c: "Container", uid: int, arg: str) -> Result:
    if not arg.strip().isdigit():
        return Result("Отправь ID пользователя (число).")
    await c.access.ban(uid, int(arg.strip()), False)
    return Result("✅ Разбанен.")


async def _audit(c: "Container", uid: int, _: str) -> Result:
    rows = await c.repos.audit.recent(25)
    if not rows:
        return Result("Записей в журнале нет.")
    return Result("<b>Последние действия</b>\n" + "\n".join(
        f"{r['created_at']} · {r['user_id']} · {r['action']} {r['detail'] or ''}" for r in rows))


# --------------------------------------------------------------------------- #
# the registry
# --------------------------------------------------------------------------- #
def _t(**kw) -> Tool:
    return Tool(**kw)

TOOLS: dict[str, Tool] = {t.id: t for t in [
    # ---- OSINT ----
    _t(id="whois", label="WHOIS", category="osint", module="osint",
       prompt="Отправь домен (например example.com)", run=_osint("whois", "WHOIS")),
    _t(id="dns", label="DNS", category="osint", module="osint",
       prompt="Отправь хост или домен", run=_osint("dns", "DNS")),
    _t(id="subdomains", label="Поддомены", category="osint", module="osint",
       prompt="Отправь домен — поищу поддомены (crt.sh)", run=_osint("subdomains", "Поддомены")),
    _t(id="username", label="Юзернейм", category="osint", module="osint",
       prompt="Отправь никнейм — поищу профили на сайтах", run=_osint("username", "Юзернейм")),
    _t(id="email", label="Почта", category="osint", module="osint",
       prompt="Отправь email-адрес", run=_osint("email", "Почта")),
    _t(id="phone", label="Телефон", category="osint", module="osint",
       prompt="Отправь номер телефона (+код страны…)", run=_osint("phone", "Телефон")),
    _t(id="geoip", label="GeoIP", category="osint", module="geoint",
       prompt="Отправь IP или хост", run=_osint("geoip", "GeoIP")),
    _t(id="shodan", label="Shodan", category="osint", module="osint",
       prompt="Отправь IP (нужен ключ Shodan)", run=_osint("shodan", "Shodan")),
    _t(id="threatintel", label="Threat Intel", category="osint", module="osint",
       prompt="Отправь IP, домен или ссылку", run=_osint("threat_intel", "Threat Intel")),
    _t(id="ioc", label="Индикатор", category="osint", module="osint",
       prompt="Отправь индикатор (IP, хеш, CVE, домен…)", run=_osint("ioc", "Индикатор")),
    _t(id="revimg", label="Поиск по фото", category="osint", module="image",
       prompt="Отправь ссылку на изображение", run=_osint("reverse_image", "Поиск по фото")),
    _t(id="exif", label="Метаданные", category="osint", module="image",
       kind="photo", prompt="Отправь фото (файлом — тогда EXIF сохранится полностью)"),
    _t(id="darknet", label="Даркнет", category="osint", module="osint",
       prompt="Отправь запрос", run=_osint("darknet", "Даркнет")),

    # ---- Pentest ----
    _t(id="portscan", label="Скан портов", category="pentest", module="recon",
       prompt="Отправь хост (только с разрешения владельца)",
       run=_pentest_native("scan_ports", "Скан портов")),
    _t(id="sslscan", label="SSL-скан", category="pentest", module="recon",
       prompt="Отправь хост", run=_pentest_native("ssl_scan", "SSL-скан")),
    _t(id="techdetect", label="Технологии", category="pentest", module="web",
       prompt="Отправь ссылку", run=_pentest_native("tech_detect", "Технологии")),
    _t(id="subfinder", label="subfinder", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("subfinder", "subfinder")),
    _t(id="amass", label="amass", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("amass", "amass")),
    _t(id="httpx", label="httpx", category="pentest", module="recon",
       prompt="Отправь ссылку или хост", run=_external("httpx", "httpx")),
    _t(id="naabu", label="naabu", category="pentest", module="recon",
       prompt="Отправь хост", run=_external("naabu", "naabu")),
    _t(id="nuclei", label="nuclei", category="pentest", module="recon",
       prompt="Отправь ссылку (только с разрешения владельца)", run=_external("nuclei", "nuclei")),
    _t(id="katana", label="katana", category="pentest", module="recon",
       prompt="Отправь ссылку", run=_external("katana", "katana")),
    _t(id="masscan", label="masscan", category="pentest", module="recon",
       prompt="Отправь хост или подсеть (только с разрешения)", run=_external("masscan", "masscan")),
    _t(id="rustscan", label="rustscan", category="pentest", module="recon",
       prompt="Отправь хост", run=_external("rustscan", "rustscan")),
    _t(id="gobuster", label="gobuster", category="pentest", module="recon",
       prompt="Отправь домен", run=_external("gobuster", "gobuster")),
    _t(id="ffuf", label="ffuf", category="pentest", module="web",
       prompt="Отправь ссылку со словом FUZZ", run=_external("ffuf", "ffuf")),
    _t(id="ferox", label="feroxbuster", category="pentest", module="web",
       prompt="Отправь ссылку", run=_external("feroxbuster", "feroxbuster")),

    # ---- AI ----
    _t(id="ai_ask", label="Спросить ИИ", category="ai", module="ai",
       prompt="Задай вопрос", run=_ai_ask),
    _t(id="ai_chat", label="Режим диалога", category="ai", module="ai", kind="chat"),
    _t(id="ai_providers", label="Провайдеры", category="ai", module="ai",
       kind="instant", run=_ai_providers),
    _t(id="ai_reset", label="Очистить историю", category="ai", module="ai",
       kind="instant", run=_ai_reset),

    # ---- Agents ----
    _t(id="ag_general", label="Универсальный", category="agents", module="ai",
       prompt="Опиши задачу", run=_agent("general", "Универсальный ассистент")),
    _t(id="ag_osint", label="OSINT", category="agents", module="ai",
       prompt="Опиши цель", run=_agent("osint", "OSINT-агент")),
    _t(id="ag_recon", label="Разведка", category="agents", module="ai",
       prompt="Опиши цель", run=_agent("recon", "Агент разведки")),
    _t(id="ag_report", label="Отчёт", category="agents", module="ai",
       prompt="Вставь находки — соберу отчёт", run=_agent("report", "Агент отчётов")),
    _t(id="ag_threat", label="Threat Intel", category="agents", module="ai",
       prompt="Отправь индикаторы", run=_agent("threatintel", "Агент Threat Intel")),
    _t(id="ag_code", label="Код", category="agents", module="ai",
       prompt="Опиши задачу по коду", run=_agent("code", "Агент по коду")),
    _t(id="ag_research", label="Ресёрч", category="agents", module="ai",
       prompt="Задай исследовательский вопрос", run=_agent("research", "Агент-исследователь")),
    _t(id="ag_planner", label="Планировщик", category="agents", module="ai",
       prompt="Опиши цель — составлю план", run=_agent("planner", "Агент-планировщик")),

    # ---- Productivity ----
    _t(id="note_add", label="➕ Заметка", category="productivity", module="notes",
       prompt="Отправь текст заметки (первая строка — заголовок)", run=_note_add),
    _t(id="note_list", label="📋 Заметки", category="productivity", module="notes",
       kind="instant", run=_note_list),
    _t(id="todo_add", label="➕ Задача", category="productivity", module="todo",
       prompt="Отправь текст задачи", run=_todo_add),
    _t(id="todo_list", label="📋 Задачи", category="productivity", module="todo",
       kind="instant", run=_todo_list),
    _t(id="todo_done", label="☑️ Выполнить", category="productivity", module="todo",
       prompt="Отправь номер задачи", run=_todo_done),

    # ---- Export ----
    _t(id="exp_pdf", label="PDF", category="export", module="reports", kind="instant", run=_export("pdf")),
    _t(id="exp_docx", label="DOCX", category="export", module="reports", kind="instant", run=_export("docx")),
    _t(id="exp_html", label="HTML", category="export", module="reports", kind="instant", run=_export("html")),
    _t(id="exp_md", label="Markdown", category="export", module="reports", kind="instant", run=_export("markdown")),
    _t(id="exp_csv", label="CSV", category="export", module="reports", kind="instant", run=_export("csv")),
    _t(id="exp_json", label="JSON", category="export", module="reports", kind="instant", run=_export("json")),

    # ---- Settings ----
    _t(id="profile", label="👤 Профиль", category="settings", module="profile",
       kind="instant", run=_profile),
    _t(id="keys", label="🔑 Ключи", category="settings", module="profile",
       kind="instant", run=_keys_list),
    _t(id="addkey", label="➕ Добавить ключ", category="settings", module="profile", kind="apikey"),
    _t(id="setprov", label="Сменить ИИ", category="settings", module="profile",
       prompt="Отправь название провайдера (openrouter, openai, claude, gemini…)",
       run=_set_provider),

    # ---- Admin ----
    _t(id="users", label="Пользователи", category="admin", module="admin",
       kind="instant", run=_users),
    _t(id="grant", label="Выдать роль", category="admin", module="admin",
       prompt="Отправь: &lt;id пользователя&gt; &lt;роль&gt;", run=_grant),
    _t(id="ban", label="Забанить", category="admin", module="admin",
       prompt="Отправь ID пользователя для бана", run=_ban),
    _t(id="unban", label="Разбанить", category="admin", module="admin",
       prompt="Отправь ID пользователя для разбана", run=_unban),
    _t(id="audit", label="Журнал", category="admin", module="audit",
       kind="instant", run=_audit),
]}


def tools_in(category: str) -> list[Tool]:
    return [t for t in TOOLS.values() if t.category == category]


def get_tool(tool_id: str) -> Tool | None:
    return TOOLS.get(tool_id)
