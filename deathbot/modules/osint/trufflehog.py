"""TruffleHog (real CLI, github.com/trufflesecurity/trufflehog) — deep secret
scanner with 800+ detectors and entropy analysis, run against pasted text.

Complements secretscan.py's offline regex list: TruffleHog checks the actual
per-provider format/checksum instead of a shape-only regex, so it has far
fewer false positives on random-looking-but-fake strings. Always run with
--no-verification: TruffleHog *can* confirm a secret is still live by calling
the provider's own API, but that means sending the pasted text's secrets to a
third party — this bot never does that without the user explicitly asking.
"""
from __future__ import annotations

import json
import os
import tempfile

from ...util import run_command

_BINARY = "trufflehog"


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 10:
        return f"{value[:2]}…" if len(value) > 4 else "…"
    return f"{value[:6]}…{value[-4:]}"


async def scan(text: str, timeout: int = 60) -> dict:
    fd, path = tempfile.mkstemp(suffix=".txt", dir="/tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", errors="replace") as f:
            f.write(text)
        result = await run_command(
            [_BINARY, "filesystem", "--no-verification", "--json", path],
            timeout=timeout, cwd="/tmp",
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    if result.missing:
        return {"available": False, "reason": f"`{_BINARY}` не установлен на хосте."}

    findings = []
    for line in (result.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{") or '"DetectorName"' not in line:
            continue  # trufflehog also emits non-JSON progress/info lines
        try:
            row = json.loads(line)
        except ValueError:
            continue
        raw = row.get("Raw", "")
        line_no = (
            row.get("SourceMetadata", {}).get("Data", {})
               .get("Filesystem", {}).get("line")
        )
        findings.append({
            "detector": row.get("DetectorName", "?"),
            "verified": bool(row.get("Verified")),
            "match": _mask(raw),
            "line": line_no,
        })

    return {
        "available": True,
        "chars_scanned": len(text),
        "count": len(findings),
        "findings": findings[:60],
    }
