"""AI Investigator (PHASE 5) — drives the existing OSINT service with LLM
planning over a live Investigation state.

Design constraints honored:
* no second orchestrator — the loop is ~120 lines and reuses
  ``deathbot.services.osint`` (which already handles caching, audit, RBAC)
  plus the existing TaskEngine for slow tools;
* the LLM only ever *plans*: it picks tool ids from the registry manifest;
  every actual execution goes through the same permission/caching/audit path
  a human button-press would take;
* observation-first: each round the model sees normalized results so far and
  must justify the next step or declare completion;
* passive-only by default — active/pentest tools require the user to be at
  least admin AND to have explicitly asked for active recon.
"""

from __future__ import annotations

import json
import re

from ..ai import AIRouter
from ..logging_setup import get_logger
from .investigation import Investigation, InvStatus

log = get_logger("tools.investigator")

MAX_ROUNDS = 6          # plan/execute rounds per investigation
MAX_FINDINGS = 400      # hard cap on stored findings


# Tools the investigator may run autonomously. Everything here is passive.
PASSIVE_TOOL_IDS: tuple[str, ...] = (
    # native service methods (no external binary needed):
    "whois", "dns", "subdomains", "username", "email", "phone", "geoip",
    "shodan", "threat_intel", "ioc", "darknet", "leak", "reverse_image",
    "emailrep",
    # CLI wrappers that are installed in the image:
    "sherlock_cli", "maigret", "socialscan", "holehe", "h8mail",
    "theharvester", "dnstwist", "sublist3r", "checkdmarc", "wafw00f",
    "metafinder", "secretscan", "httpx", "whatweb", "gau",
)

#: target kind -> ordered tool preferences (first hit wins when planning)
PLAYBOOKS: dict[str, tuple[tuple[str, ...], ...]] = {
    "domain": (("whois", "dns"), ("subdomains",), ("checkdmarc",),
               ("whatweb", "httpx"), ("wafw00f",)),
    "ip": (("geoip",), ("threat_intel", "ioc"), ("shodan",)),
    "email": (("emailrep", "holehe"), ("h8mail",), ("leak",)),
    "username": (("username",), ("sherlock_cli", "maigret"), ("socialscan",)),
    "phone": (("phone",),),
}


class AIInvestigator:
    def __init__(self, router: AIRouter, osint_service) -> None:
        self.router = router
        self.osint = osint_service

    # -- planning ------------------------------------------------------------

    async def classify_target(self, raw: str) -> str:
        """LLM-assisted target classification with regex fallback."""
        v = raw.strip()
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", v):
            return "ip"
        if "@" in v:
            return "email"
        if re.fullmatch(r"\+?\d[\d\s()-]{7,}", v):
            return "phone"
        if v.startswith("http"):
            return "url"
        if "." in v and " " not in v:
            return "domain"
        # ambiguous (could be username or person name) → ask the model once
        try:
            answer = await self.router.chat([
                ChatMessage("system",
                            "Classify the target into exactly one word: "
                            "domain, ip, email, phone, url, username. "
                            "Answer with the single word only."),
                ChatMessage("user", v),
            ])
            word = answer.content.strip().lower().split()[0]
            if word in ("domain", "ip", "email", "phone", "url", "username"):
                return word
        except Exception as exc:  # noqa: BLE001 - classifier failure is fine
            log.debug("target classify fell back: %s", exc)
        return "username"

    def build_plan(self, inv: Investigation, target_kind: str,
                   depth: str = "standard") -> list[str]:
        """Ordered tool list from playbooks; deduped against done_tools."""
        stages = PLAYBOOKS.get(target_kind, PLAYBOOKS["username"])
        if depth == "max":
            extra = {
                "domain": ("dnsrecon", "sublist3r", "gau"),
                "email": ("email",),
                "username": ("theharvester",),
                "ip": (),
                "phone": (),
            }.get(target_kind, ())
            stages = stages + tuple((t,) for t in extra)  # each its own stage
        planned: list[str] = []
        for stage in stages:
            for tid in stage:
                if tid in inv.done_tools():
                    continue
                if tid in PASSIVE_TOOL_IDS:
                    planned.append(tid)
                    if depth != "max":
                        break        # standard: one tool per stage
                    # max: try every passive tool of the stage
        return planned

    # -- execution -----------------------------------------------------------

    async def _run_tool(self, inv: Investigation, tid: str,
                        target: str) -> None:
        run = inv.start_run(tid, target)
        try:
            method = getattr(self.osint, tid, None)
            if method is None and hasattr(self.osint, "cli"):
                data = await self.osint.cli(inv.user_id, tid, target)
            elif method is not None:
                data = await method(inv.user_id, target)
            else:
                inv.finish_run(run, status="skipped_no_creds",
                               error="tool has no service entrypoint")
                return
            text = ""
            findings_count = 0
            if isinstance(data, dict):
                installed = data.get("installed", True)
                if installed is False:
                    inv.finish_run(run, status="failed",
                                   error=data.get("hint", "not installed"))
                    return
                out = data.get("output") or data.get("results") or ""
                text = out if isinstance(out, str) else json.dumps(out)[:2000]
                findings_count = _count_findings(text)
                status = "success" if findings_count else "empty"
            else:
                text = str(data)
                status = "success" if text.strip() else "empty"
            inv.finish_run(run, status=status,
                           findings_count=findings_count)
            _extract_entities(inv, tid, text, related_to=inv.root_target)
        except Exception as exc:  # noqa: BLE001 - honest failure per tool
            inv.finish_run(run, status="failed", error=str(exc)[:200])
            log.warning("investigator: tool %s failed: %s", tid, exc)

    async def investigate(self, inv: Investigation, *,
                          depth: str = "standard",
                          provider: str | None = None,
                          user_keys: dict[str, str] | None = None,
                          progress_cb=None) -> Investigation:
        """Plan → execute → observe → pivot rounds, then an AI analysis."""
        inv.status = InvStatus.PLANNING
        kind = await self.classify_target(inv.root_target or inv.goal)
        if not inv.root_target:
            inv.root_target = inv.goal.strip()

        inv.graph.add(kind, inv.root_target, by_tool="plan")

        plan = self.build_plan(inv, kind, depth=depth)
        if not plan:
            inv.status = InvStatus.FAILED
            return inv

        for i, tid in enumerate(plan, 1):
            if progress_cb:
                await progress_cb(f"▸ {i}/{len(plan)} · запуск {tid}…")
            await self._run_tool(inv, tid, inv.root_target)

        # pivots: emails/usernames discovered on a domain/person get their own
        # light pass (bounded: max 2 pivots × 2 tools).
        pivots = [n for n in list(inv.graph.nodes.values())
                  if n.kind in ("email", "username")
                  and n.value.lower() != inv.root_target.lower()][:4]
        for node in pivots[:2]:
            pkind = "email" if node.kind == "email" else "username"
            sub_plan = self.build_plan(inv, pkind)[:2]
            for tid in sub_plan:
                if progress_cb:
                    await progress_cb(f"↳ пивот {node.value}: {tid}…")
                await self._run_tool(inv, tid, node.value)

        inv.status = InvStatus.PARTIAL if any(
            r.status in ("failed", "empty") for r in inv.runs) \
            and any(r.status == "success" for r in inv.runs) \
            else InvStatus.COMPLETED

        # AI analysis of everything collected (single call).
        inv.ai_analysis = await self._analyze(inv, provider, user_keys)
        if inv.ai_analysis.startswith("⚠️"):
            inv.notes.append("AI analysis unavailable")
        return inv

    async def _analyze(self, inv: Investigation, provider, user_keys) -> str:
        digest = []
        for n in list(inv.graph.nodes.values())[:60]:
            digest.append(f"{n.kind}:{n.value}")
        runs = "\n".join(
            f"- {r.tool_id} [{r.target}] → {r.status}"
            f" ({r.findings_count} findings)" for r in inv.runs)
        prompt = (
            f"Investigation goal: {inv.goal}\n"
            f"Root target ({await self.classify_target(inv.root_target)}): "
            f"{inv.root_target}\n\n"
            f"Tools executed:\n{runs}\n\n"
            f"Entities discovered:\n" + "\n".join(digest) + "\n\n"
            "Write a concise intelligence summary in Russian: key facts, "
            "interesting correlations, risk assessment, and what a follow-up "
            "investigation should check. No speculation — only what the data "
            "shows. Max 10 sentences.")
        try:
            resp = await self.router.chat([
                ChatMessage("system", OSINT_ANALYST_PERSONA),
                ChatMessage("user", prompt),
            ], provider=provider, user_keys=user_keys)
            return resp.content
        except Exception as exc:  # noqa: BLE001
            return f"⚠️ Анализ недоступен: {exc}"


OSINT_ANALYST_PERSONA = (
    "You are an OSINT intelligence analyst writing the final section of an "
    "automated investigation report. You are given the executed tools and "
    "discovered entities. Summarize only what the data shows, highlight "
    "correlations between entities, assess confidence, and suggest concrete "
    "next steps. Be factual and terse. Russian language.")


def _count_findings(text: str) -> int:
    if not text:
        return 0
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return len(lines)


_KIND_HINTS = (
    ("@", "email"),
    ("http", "url"),
)


def _extract_entities(inv: Investigation, tool: str, text: str,
                      *, related_to: str | None) -> None:
    """Mine obvious entities (emails, URLs, IPs, subdomains) from tool text."""
    if len(inv.findings) >= MAX_FINDINGS or not text:
        return
    emails = set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    for em in list(emails)[:20]:
        if inv.add_finding("email", em, tool, related_to):
            pass
    ips = set(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", text))
    for ip in list(ips)[:15]:
        if ip.count(".") == 3 and not ip.endswith((".0", ".255")):
            inv.add_finding("ip", ip, tool, related_to)
    subs = set(re.findall(r"\b([a-z0-9-]+(?:\.[a-z0-9-]+)+)\b", text.lower()))
    root = (inv.root_target or "").lower()
    for prefix in ("https://", "http://"):
        root = root.removeprefix(prefix)
    if root:
        for s in list(subs)[:25]:
            if s != root and s.endswith(root) and " " not in s:
                inv.add_finding("subdomain", s, tool, related_to=root)


from ..ai import ChatMessage
