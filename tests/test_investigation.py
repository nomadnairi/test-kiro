"""Investigation state + AI investigator planning (H2/Multi-OSINT Hub).

Pinned contracts:
* entity graph dedupes and links pivots;
* playbooks pick passive tools per target kind and skip already-run ones;
* a failing/empty tool run is recorded honestly and never counted as success;
* the report card contains the sections the user sees in Telegram.
"""

from __future__ import annotations

import pytest

from deathbot.tools.investigation import (
    EntityGraph,
    InvStatus,
    Investigation,
    kind_guess,
)
from deathbot.tools.investigator import AIInvestigator


# ---------------------------------------------------------------------------
# Entity graph
# ---------------------------------------------------------------------------

def test_graph_dedupes_entities():
    g = EntityGraph()
    assert g.add("email", "a@x.com", "holehe") is True
    assert g.add("email", "a@x.com", "h8mail") is False   # duplicate
    node = g.nodes["email:a@x.com"]
    assert sorted(node.discovered_by) == ["h8mail", "holehe"]


def test_graph_links_pivot_to_source():
    g = EntityGraph()
    g.add("domain", "example.com", "plan")
    g.add("ip", "93.184.216.34", "dns", related_to="example.com")
    assert ("domain:example.com", "resolved_from",
            "ip:93.184.216.34") in [(s, r, d) for s, r, d in g.edges]


def test_kind_guess():
    assert kind_guess("1.2.3.4") == "ip"
    assert kind_guess("a@b.com") == "email"
    assert kind_guess("https://x.y/z") == "url"
    assert kind_guess("ex.com") == "domain"
    assert kind_guess("john_doe") == "username"


# ---------------------------------------------------------------------------
# Playbook planning
# ---------------------------------------------------------------------------

def _inv(target: str):
    inv = Investigation(chat_id=1, user_id=2, goal=f"check {target}",
                        root_target=target)
    return inv


@pytest.mark.asyncio
async def test_classify_domain_and_ip():
    from deathbot.ai import AIRouter
    router = AIRouter.__new__(AIRouter)      # no provider calls needed
    investigator = AIInvestigator(router, osint_service=None)

    assert await investigator.classify_target("example.com") == "domain"
    assert await investigator.classify_target("192.168.0.1") == "ip"
    assert await investigator.classify_target("+7 999 123-45-67") == "phone"
    assert await investigator.classify_target("a@b.co") == "email"


def _plan(inv, kind, depth="standard"):
    from deathbot.ai import AIRouter
    investigator = AIInvestigator(AIRouter.__new__(AIRouter), None)
    return investigator.build_plan(inv, kind, depth=depth)


def test_plan_domain_is_passive_ordered():
    inv = _inv("example.com")
    plan = _plan(inv, "domain")
    assert plan, "domain playbook produced nothing"
    assert all(t in ("whois", "dns", "subdomains", "checkdmarc",
                     "whatweb", "httpx", "wafw00f") for t in plan)


def test_plan_skips_already_run_tools():
    inv = _inv("example.com")
    inv.start_run("dns", "example.com")
    inv.runs[0].status = "success"
    plan = _plan(inv, "domain")
    assert "dns" not in plan


def test_plan_max_depth_adds_extras():
    inv = _inv("example.com")
    std = _plan(inv, "domain", depth="standard")
    mx = _plan(inv, "domain", depth="max")
    assert len(mx) >= len(std)
    assert any(t in mx for t in ("dnsrecon", "sublist3r"))


# ---------------------------------------------------------------------------
# Honest run bookkeeping
# ---------------------------------------------------------------------------

def test_failed_tool_not_counted_as_success():
    inv = _inv("example.com")
    run = inv.start_run("subfinder", "example.com")
    inv.finish_run(run, status="failed", error="not installed")
    ok = [r for r in inv.runs if r.status == "success"]
    assert not ok
    assert inv.runs[0].error == "not installed"


def test_report_card_sections():
    inv = _inv("example.com")
    run = inv.start_run("dns", "example.com")
    inv.finish_run(run, findings_count=4, status="success", duration_ms=120)
    inv.add_finding("ip", "1.2.3.4", "dns", related_to="example.com")
    card = inv.report_card()
    assert "OSINT INVESTIGATION" in card
    assert "example.com" in card
    assert "✅ dns" in card
    assert "ip: 1" in card or "├─ ip" in card
