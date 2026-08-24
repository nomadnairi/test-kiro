"""Unified result model (PHASE 4) + professional report renderer (PHASE 9).

Every tool result is normalized into a ToolResultRecord before it reaches the
AI investigator or a report, so the model never has to parse raw stdout.
Confidence labels distinguish what is proven from what is merely likely —
an assumption must never be presented as a fact.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    NO_RESULT = "NO_RESULT"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    DENIED = "DENIED"


class Confidence(str, Enum):
    CONFIRMED = "CONFIRMED"    # tool output states it directly
    LIKELY = "LIKELY"          # strong signal, indirect evidence
    POSSIBLE = "POSSIBLE"      # weak/circumstantial
    UNKNOWN = "UNKNOWN"


@dataclass
class ToolResultRecord:
    """The unified structured result every execution produces."""

    tool: str
    target: str
    started_at: float = field(default_factory=time.time)
    finished_at: float = 0.0
    status: RunStatus = RunStatus.SUCCESS
    confidence: Confidence = Confidence.CONFIRMED
    findings: list[dict] = field(default_factory=list)   # {kind,value,context}
    errors: list[str] = field(default_factory=list)
    raw_output_reference: str = ""                       # audit-log id / path
    metadata: dict = field(default_factory=dict)

    def finalize(self) -> ToolResultRecord:
        self.finished_at = time.time()
        if not self.finished_at:
            self.finished_at = time.time()
        return self

    @property
    def duration_ms(self) -> int:
        return int((self.finished_at - self.started_at) * 1000)

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "target": self.target,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "findings": self.findings[:200],
            "findings_total": len(self.findings),
            "errors": self.errors,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# PHASE 9 — Telegram intelligence report renderer
# ---------------------------------------------------------------------------

_CONFIDENCE_ORDER = ("CONFIRMED", "LIKELY", "POSSIBLE", "UNKNOWN")


def render_report(inv, page: int = 0, per_page: int = 14) -> str:
    """Render an Investigation as a formatted Telegram intelligence report.

    ``inv`` is deathbot.tools.investigation.Investigation. Long finding
    lists are paginated; the summary always stays on page 1.
    """
    title = inv.root_target or inv.goal[:40]
    lines: list[str] = [
        "╭──────────────────────────────╮",
        "│ 🔎 OSINT INVESTIGATION       │",
        f"│ {title[:28]:<28} │",
        "╰──────────────────────────────╯",
        "",
        f"🎯 TARGET: {inv.root_target or '—'}",
        f"🆔 ID: <code>{inv.id}</code>",
        f"📊 STATUS: {inv.status.value.upper()}   ⏱ {inv.elapsed_s:.1f}s",
        "",
    ]

    counts = inv.summary_counts()
    ok = [r for r in inv.runs if r.status == "success"]
    total_findings = sum(r.findings_count for r in inv.runs)
    risk = _risk_of(inv)
    lines.append("📊 SUMMARY")
    lines.append(f"├─ Risk: {risk}")
    conf = _overall_confidence(inv)
    lines.append(f"├─ Confidence: {conf}")
    lines.append(f"└─ Findings: {total_findings}")
    lines.append("")

    if counts:
        lines.append("🌐 INTELLIGENCE")
        items = list(counts.items())
        start = 0 if page == 0 else per_page * page - 2
        chunk = items[start:start + per_page] if page else items[:per_page]
        for kind, cnt in chunk:
            lines.append(f"├─ {kind}: {cnt}")
        pages = max(1, -(-len(items) // per_page))
        if pages > 1:
            lines.append(f"└─ ◀ страница {min(page + 1, pages)}/{pages} ▶")
        lines.append("")

    lines.append("🧰 TOOLS EXECUTED")
    for r in ok:
        lines.append(f"├─ ✅ {r.tool_id}: {r.findings_count} findings")
    for r in inv.runs:
        if r.status in ("empty",):
            lines.append(f"├─ ➖ {r.tool_id}: no data")
        elif r.status in ("failed", "denied"):
            lines.append(f"├─ ❌ {r.tool_id}: {(r.error or r.status)[:40]}")
    lines.append("")
    lines.append(f"🔗 Relationships: {len(inv.graph.edges)}")

    if inv.ai_analysis:
        lines.append("")
        lines.append("🧠 AI ANALYSIS")
        lines.append(inv.ai_analysis[:1500])

    return "\n".join(lines)


def _overall_confidence(inv) -> str:
    confirmed = sum(1 for n in inv.graph.nodes.values() if len(n.discovered_by) >= 2)
    total = max(1, len(inv.graph.nodes))
    pct = min(95, 40 + round(confirmed / total * 60))
    return f"{pct}% ({confirmed} cross-verified)"


def _risk_of(inv) -> str:
    text = (inv.ai_analysis or "").lower()
    if any(w in text for w in ("critical", "критический")):
        return "HIGH"
    if any(w in text for w in ("leak", "breach", "утечк", "exposed", "vulnerab")):
        return "MEDIUM"
    if any(r.status == "failed" for r in inv.runs) and any(
            r.status == "success" for r in inv.runs):
        return "LOW-MEDIUM"
    return "LOW"
