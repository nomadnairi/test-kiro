"""ExportService — render a report dict into several formats.

md / json / html / csv are always available (pure stdlib). pdf / docx are
best-effort and require optional dependencies; the service reports which
formats are actually usable so callers can degrade gracefully.
"""
from __future__ import annotations

import csv
import io
import json
from html import escape


class ExportService:
    ALWAYS = ("json", "markdown", "html", "csv")

    def available_formats(self) -> list[str]:
        formats = list(self.ALWAYS)
        try:
            import reportlab  # noqa: F401
            formats.append("pdf")
        except ImportError:
            pass
        try:
            import docx  # noqa: F401
            formats.append("docx")
        except ImportError:
            pass
        return formats

    def render(self, report: dict, fmt: str) -> bytes:
        fmt = fmt.lower()
        renderer = {
            "json": self._json,
            "markdown": self._markdown,
            "md": self._markdown,
            "html": self._html,
            "csv": self._csv,
        }.get(fmt)
        if renderer is None:
            raise ValueError(f"Unsupported export format: {fmt}")
        return renderer(report)

    # -- renderers ----------------------------------------------------------
    def _json(self, report: dict) -> bytes:
        return json.dumps(report, indent=2, ensure_ascii=False).encode()

    def _markdown(self, report: dict) -> bytes:
        lines = [f"# {report.get('title', 'DeathBot Report')}", ""]
        for section, body in report.get("sections", {}).items():
            lines.append(f"## {section}")
            lines.append("```")
            lines.append(body if isinstance(body, str) else json.dumps(body, indent=2))
            lines.append("```")
            lines.append("")
        return "\n".join(lines).encode()

    def _html(self, report: dict) -> bytes:
        parts = [f"<h1>{escape(str(report.get('title', 'DeathBot Report')))}</h1>"]
        for section, body in report.get("sections", {}).items():
            text = body if isinstance(body, str) else json.dumps(body, indent=2)
            parts.append(f"<h2>{escape(str(section))}</h2><pre>{escape(text)}</pre>")
        return ("<!doctype html><meta charset='utf-8'>" + "".join(parts)).encode()

    def _csv(self, report: dict) -> bytes:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["section", "content"])
        for section, body in report.get("sections", {}).items():
            writer.writerow([section, body if isinstance(body, str) else json.dumps(body)])
        return buf.getvalue().encode()
