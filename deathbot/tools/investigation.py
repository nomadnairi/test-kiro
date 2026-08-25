"""Investigation runtime state (H2/Multi-OSINT Hub 2.0, PHASE 6)."""
from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


def _now() -> float:
    return time.time()


class Confidence(str, Enum):
    CONFIRMED = "CONFIRMED"      # ≥2 независимых источника или прямое указание
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


@dataclass
class Evidence:
    tool: str
    detail: str = ""
    at: float = field(default_factory=lambda: time.time())


class InvStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ToolRun:
    tool_id: str
    target: str
    status: str = "pending"          # pending|running|success|empty|failed|skipped_no_creds|denied
    findings_count: int = 0
    duration_ms: int = 0
    error: str = ""
    started_at: float = field(default_factory=_now)


@dataclass
class Finding:
    """One atomic fact produced by a tool."""

    tool: str
    kind: str                        # ip|email|username|domain|subdomain|url|asn|tech|cert|breach|…
    value: str
    context: str = ""                # short human hint from the tool output
    confidence: float = 0.8


@dataclass
class Entity:
    """A node in the correlation graph."""

    kind: str
    value: str
    discovered_by: list[str] = field(default_factory=list)   # tool ids
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.LOW

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.value.lower()}"

    def add_evidence(self, tool: str, detail: str = "") -> None:
        self.evidence.append(Evidence(tool=tool, detail=detail))
        if tool not in self.discovered_by:
            self.discovered_by.append(tool)
        # Confidence grows with the number of independent sources.
        sources = len({e.tool for e in self.evidence})
        if sources >= 2 or any(
                e.tool in ("whois", "dns", "shodan") for e in self.evidence):
            self.confidence = Confidence.CONFIRMED
        elif sources == 1 and self.evidence[0].tool in (
                "subfinder", "httpx", "whatweb"):
            self.confidence = Confidence.MEDIUM


class EntityGraph:
    """Entities + typed edges, built up as results come in."""

    def __init__(self) -> None:
        self.nodes: dict[str, Entity] = {}
        # (src_key, relationship, dst_key, evidence_tool, confidence)
        self.edges: list[tuple[str, str, str, str, Confidence]] = []
        self.conflicts: list[dict] = []               # contradictory findings

    def add(self, kind: str, value: str, by_tool: str,
            related_to: str | None = None, rel: str = "resolved_from") -> bool:
        """Add an entity; returns False when it already existed (dedupe).

        ``related_to`` is the raw value of the entity this one was found via;
        it is resolved to its node key when known so the graph stays connected.
        """
        e = Entity(kind=kind, value=value, discovered_by=[by_tool])
        existed = e.key in self.nodes
        if existed:
            self.nodes[e.key].discovered_by.append(by_tool)
        else:
            self.nodes[e.key] = e
        if related_to is not None:
            src = f"{kind_guess(related_to)}:{related_to.lower()}"
            if src not in self.nodes:
                src = related_to.lower()
            self.edges.append((src, rel, e.key, by_tool, Confidence.LOW))
        return not existed

    def report_conflict(self, subject: str, aspect: str,
                        values: dict[str, str]) -> None:
        """Two tools disagree about the same fact — recorded with sources,
        never resolved by coin-flip."""
        self.conflicts.append({"subject": subject, "aspect": aspect,
                               "claims": values})

    def related(self, key: str) -> list[str]:
        out = []
        for s, _rel, d, _t, _c in self.edges:
            if s == key:
                out.append(d)
            elif d == key:
                out.append(s)
        return out


def self_nodes_keys():  # pragma: no cover - helper kept tiny
    return []


class Investigation:
    """Full state of one investigation session."""

    def __init__(self, chat_id: int, user_id: int, goal: str,
                 root_target: str = "") -> None:
        self.id = uuid.uuid4().hex[:10]
        self.chat_id = chat_id
        self.user_id = user_id
        self.goal = goal
        self.root_target = root_target
        self.status = InvStatus.CREATED
        self.created_at = time.time()
        self.graph = EntityGraph()
        self.runs: list[ToolRun] = []
        self.findings: list[Finding] = []
        self.ai_analysis: str = ""
        self.notes: list[str] = []

    # -- bookkeeping --------------------------------------------------------

    def start_run(self, tool_id: str, target: str) -> ToolRun:
        run = ToolRun(tool_id=tool_id, target=target, status="running")
        self.runs.append(run)
        self.status = InvStatus.RUNNING
        return run

    def finish_run(self, run: ToolRun, *, findings_count: int = 0,
                   status: str = "success", error: str = "",
                   duration_ms: int = 0) -> None:
        run.status = status
        run.findings_count = findings_count
        run.error = error
        run.duration_ms = duration_ms or round(
            (time.time() - run.started_at) * 1000)

    def add_finding(self, kind: str, value: str, tool: str,
                    related_to: str | None = None,
                    context: str = "") -> bool:
        """Register a finding + graph node; returns True when new.

        Repeats are not discarded blindly: each repeat strengthens the
        entity's evidence list (cross-verification), only the findings log
        stays deduplicated.
        """
        node_key = f"{kind}:{value.lower()}"
        seen_before = node_key in self.graph.nodes
        self.graph.add(kind, value, tool, related_to)
        node = self.graph.nodes.get(node_key)
        if node is not None:
            node.add_evidence(tool, context[:80])
        if not seen_before:
            self.findings.append(Finding(tool=tool, kind=kind, value=value,
                                         context=context))
        return not seen_before

    def done_tools(self) -> set[str]:
        """Tool ids already executed against a given target context — used to
        avoid pointless repeats within one investigation."""
        return {r.tool_id for r in self.runs
                if r.status in ("success", "empty")}

    def summary_counts(self) -> dict[str, int]:
        kinds: dict[str, int] = {}
        for n in self.graph.nodes.values():
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
        return dict(sorted(kinds.items(), key=lambda kv: -kv[1]))

    @property
    def elapsed_s(self) -> float:
        return time.time() - self.created_at

    # -- rendering ----------------------------------------------------------

    def progress_line(self) -> str:
        ok = sum(1 for r in self.runs if r.status == "success")
        total = len(self.runs)
        return f"🧰 {total} tools · ✅ {ok} · 🔎 {len(self.graph.nodes)} entities"

    def report_card(self) -> str:
        """Compact intelligence-report card for Telegram (PHASE 10)."""
        title = self.root_target or (self.goal[:40] + ("…" if len(self.goal) > 40 else ""))
        lines = [
            "╭──────────────────────────────╮",
            "│ 🔎 OSINT INVESTIGATION       │",
            f"│ {title[:28]:<28} │",
            "╰──────────────────────────────╯",
            "",
            f"🎯 TARGET: {self.root_target or '—'}",
            f"📊 STATUS: {self.status.value.upper()}   ⏱ {self.elapsed_s:.1f}s",
            "",
        ]
        counts = self.summary_counts()
        if counts:
            lines.append("🌐 FINDINGS BY TYPE")
            for kind, cnt in list(counts.items())[:8]:
                lines.append(f"├─ {kind}: {cnt}")
            lines.append("")
        ok_runs = [r for r in self.runs if r.status == "success"]
        empty = [r for r in self.runs if r.status == "empty"]
        failed = [r for r in self.runs if r.status == "failed"]
        lines.append("🧰 TOOLS EXECUTED")
        for r in ok_runs:
            lines.append(f"├─ ✅ {r.tool_id}: {r.findings_count} findings")
        for r in empty:
            lines.append(f"├─ ➖ {r.tool_id}: no data")
        for r in failed:
            lines.append(f"├─ ❌ {r.tool_id}: {r.error[:40]}")
        skipped = [r for r in self.runs if r.status.startswith("skipped")]
        if skipped:
            lines.append(f"├─ ⏭ skipped: {len(skipped)} (dedupe)")
        lines.append("")
        # Top cross-verified entities with evidence sources.
        verified = sorted(
            (n for n in self.graph.nodes.values()
             if len(n.discovered_by) >= 2),
            key=lambda n: -len(n.discovered_by))[:5]
        if verified:
            lines.append("🔗 KEY CORRELATIONS (evidence-backed)")
            for n in verified:
                srcs = ", ".join(sorted(set(n.discovered_by)))
                lines.append(
                    f"├─ {n.kind} {n.value} ← [{srcs}] "
                    f"({n.confidence.value})")
            lines.append("")
        if self.graph.conflicts:
            lines.append("⚠️ CONFLICTS")
            for c in self.graph.conflicts[:3]:
                claims = " vs ".join(
                    f"{t}:{v}" for t, v in c["claims"].items())
                lines.append(f"├─ {c['subject']} · {c['aspect']}: {claims}")
            lines.append("")
        lines.append(f"🔗 Total relationships: {len(self.graph.edges)}")
        if self.ai_analysis:
            lines.append("")
            lines.append("🧠 AI ANALYSIS")
            lines.append(self.ai_analysis[:1200])
        return "\n".join(lines)


# -- registry of live investigations (per chat) ------------------------------

_live: dict[int, Investigation] = {}


def open_investigation(chat_id: int, user_id: int, goal: str,
                       root_target: str = "") -> Investigation:
    inv = Investigation(chat_id, user_id, goal, root_target)
    _live[chat_id] = inv
    return inv


def current(chat_id: int) -> Investigation | None:
    return _live.get(chat_id)


def close(chat_id: int) -> None:
    _live.pop(chat_id, None)


def kind_guess(value: str) -> str:
    """Cheap entity-kind guess for edge endpoints (findings carry exact kinds;
    this only labels pivot sources that were given as raw strings)."""
    v = (value or "").strip().lower()
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", v):
        return "ip"
    if "@" in v:
        return "email"
    if v.startswith("http"):
        return "url"
    if "." in v and " " not in v:
        return "domain"
    return "username"
