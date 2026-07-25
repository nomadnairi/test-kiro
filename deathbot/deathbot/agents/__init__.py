"""A small registry of specialised agents."""
from __future__ import annotations

from ..ai import AIRouter
from .base import Agent


class GeneralAssistant(Agent):
    name = "general"
    persona = "You are DeathBot, a concise, accurate general assistant."


class OSINTAgent(Agent):
    name = "osint"
    persona = (
        "You are an OSINT analyst. Given a target, outline what public sources to "
        "check and how to correlate the findings. Be practical and lawful."
    )


class ReconAgent(Agent):
    name = "recon"
    persona = (
        "You are a reconnaissance planner. Produce an ordered, tool-by-tool recon "
        "plan (passive first) for the given authorised target."
    )


class ReportAgent(Agent):
    name = "report"
    persona = (
        "You are a report writer. Turn raw findings into a clear, structured "
        "executive summary with sections and severity."
    )


class ThreatIntelAgent(Agent):
    name = "threatintel"
    persona = (
        "You are a threat-intelligence analyst. Assess indicators (IPs, domains, "
        "hashes, CVEs), map to likely TTPs (MITRE ATT&CK) and give a risk verdict."
    )


class CodeAgent(Agent):
    name = "code"
    persona = (
        "You are a senior security engineer. Write, review and explain code and "
        "scripts. Prefer safe, idiomatic solutions and point out vulnerabilities."
    )


class ResearchAgent(Agent):
    name = "research"
    persona = (
        "You are a research assistant. Break a question into sub-questions, reason "
        "step by step, and produce a sourced, structured briefing."
    )


class PlannerAgent(Agent):
    name = "planner"
    persona = (
        "You are an engagement planner. Turn an objective into an ordered, phased "
        "action plan with tools, prerequisites and success criteria."
    )


def build_agents(router: AIRouter) -> dict[str, Agent]:
    return {a.name: a for a in (
        GeneralAssistant(router),
        OSINTAgent(router),
        ReconAgent(router),
        ReportAgent(router),
        ThreatIntelAgent(router),
        CodeAgent(router),
        ResearchAgent(router),
        PlannerAgent(router),
    )}


__all__ = [
    "Agent", "GeneralAssistant", "OSINTAgent", "ReconAgent", "ReportAgent",
    "ThreatIntelAgent", "CodeAgent", "ResearchAgent", "PlannerAgent", "build_agents",
]
