"""ReportService — assemble a normalized report structure from raw findings."""
from __future__ import annotations

import json
from datetime import datetime, timezone


class ReportService:
    def build(self, title: str, findings: dict[str, object]) -> dict:
        sections = {
            name: (value if isinstance(value, str) else json.dumps(value, indent=2))
            for name, value in findings.items()
        }
        return {
            "title": title,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": sections,
        }
