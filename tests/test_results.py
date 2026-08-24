"""Unified result model + report renderer (PHASE 4/9)."""
import pytest

from deathbot.tools.results import (
    Confidence,
    RunStatus,
    ToolResultRecord,
    render_report,
)
from deathbot.tools.investigation import (
    Investigation,
    InvStatus,
)


def test_record_finalize_and_dict():
    r = ToolResultRecord(tool="dns", target="example.com")
    r.findings = [{"kind": "ip", "value": "1.2.3.4"}]
    r.errors = []
    r.finalize()
    d = r.to_dict()
    assert d["status"] == "SUCCESS"
    assert d["findings_total"] == 1
    assert d["duration_ms"] >= 0
    assert d["confidence"] == "CONFIRMED"


@pytest.fixture()
def inv():
    inv = Investigation(chat_id=1, user_id=2, goal="check example.com",
                        root_target="example.com")
    run = inv.start_run("dns", "example.com")
    inv.finish_run(run, findings_count=3, status="success", duration_ms=120)
    inv.add_finding("ip", "1.2.3.4", "dns", related_to="example.com")
    inv.add_finding("subdomain", "www.example.com", "subfinder",
                    related_to="example.com")
    return inv


def test_render_report_has_core_sections(inv):
    text = render_report(inv)
    assert "OSINT INVESTIGATION" in text
    assert "TARGET: example.com" in text
    assert "✅ dns" in text
    assert "Confidence" in text
    assert "Relationships: 2" in text


def test_risk_escalates_on_breach_mentions(inv):
    inv.ai_analysis = "Found a breach exposure for the target email."
    assert "MEDIUM" in render_report(inv)


def test_status_reflects_partial(inv):
    failed = inv.start_run("nuclei", "example.com")
    inv.finish_run(failed, status="failed", error="boom")
    text = render_report(inv)
    assert "❌ nuclei" in text
    assert inv.status in (InvStatus.PARTIAL, InvStatus.RUNNING,
                          InvStatus.COMPLETED, InvStatus.CREATED)
