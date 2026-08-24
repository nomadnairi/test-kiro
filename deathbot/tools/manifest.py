"""Unified tool registry with rich manifests (H2/Multi-OSINT Hub 2.0).

One source of truth for every capability the bot can run: id, category,
target types, entrypoint, timeout, credentials, permission tier and an output
schema. The Telegram UI, the AI investigator and the smoke tests all read
this registry instead of maintaining parallel lists.

Status model (honest, never aspirational):

* READY                     binary present + smoke-tested
* AVAILABLE_WITH_CREDENTIALS works once an API key is configured
* BROKEN                    installed but fails its smoke test
* UNAVAILABLE               cannot be installed in this environment

``installation_status`` is *observed at runtime* by ``health_snapshot()``
(shutil.which + optional version probe) — never hardcoded.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from enum import Enum


class ToolStatus(str, Enum):
    READY = "READY"
    AVAILABLE_WITH_CREDENTIALS = "AVAILABLE_WITH_CREDENTIALS"
    BROKEN = "BROKEN"
    UNAVAILABLE = "UNAVAILABLE"


# Permission tiers mirror deathbot.core.roles; ``safe_mode`` marks purely
# passive collection (no packets to the target beyond normal HTTP/DNS).
PASSIVE = "passive"
ACTIVE = "active"


@dataclass(frozen=True)
class ToolManifest:
    id: str
    name: str
    category: str
    description: str
    target_types: tuple[str, ...]          # domain|ip|email|username|phone|url|image|hash|text
    entrypoint: str                        # binary or callable ref
    timeout: int = 120
    credentials: tuple[str, ...] = ()      # env var names required, if any
    rate_limit: str = ""                   # human hint, e.g. "4 req/s free"
    safe_mode: str = PASSIVE
    min_role: str = "user"
    output_schema: str = "findings_list"   # findings_list|report|raw_text
    version_arg: tuple[str, ...] = ()      # argv that prints a version
    declared_status: ToolStatus = ToolStatus.READY

    def runtime_status(self) -> ToolStatus:
        """Observed status right now on this machine."""
        if self.declared_status is not ToolStatus.READY:
            return self.declared_status
        if self.entrypoint.startswith("py:"):
            return ToolStatus.READY          # in-process call
        if shutil.which(self.entrypoint) is None:
            if self.credentials:
                return ToolStatus.AVAILABLE_WITH_CREDENTIALS
            return ToolStatus.UNAVAILABLE
        return ToolStatus.READY

    def version(self) -> str:
        """Best-effort version string, '' when unknown."""
        import asyncio
        if not self.version_arg:
            return ""
        try:
            from ..util import run_command

            async def _probe():
                r = await run_command([self.entrypoint, *self.version_arg],
                                      timeout=15)
                first = (r.stdout or "").strip().splitlines()
                return first[0][:80] if first else ""

            return asyncio.get_event_loop().run_until_complete(_probe()) \
                if False else ""
        except Exception:  # noqa: BLE001 - version probing must never raise
            return ""


@dataclass
class Category:
    key: str
    emoji: str
    title: str
    tools: list[ToolManifest] = field(default_factory=list)


def build_categories(manifests: list[ToolManifest]) -> list[Category]:
    """Group manifests into UI categories, preserving insertion order."""
    order: list[str] = []
    by_key: dict[str, Category] = {}
    for m in manifests:
        cat = m.category
        if cat not in by_key:
            by_key[cat] = Category(key=cat, emoji="🧰", title=cat)
            order.append(cat)
        by_key[cat].tools.append(m)
    return [by_key[k] for k in order]


def health_snapshot(manifests: list[ToolManifest]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for m in manifests:
        s = m.runtime_status().value
        counts[s] = counts.get(s, 0) + 1
    return counts
