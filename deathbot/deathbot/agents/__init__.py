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


def build_agents(router: AIRouter) -> dict[str, Agent]:
    return {a.name: a for a in (
        GeneralAssistant(router),
        OSINTAgent(router),
        ReconAgent(router),
        ReportAgent(router),
    )}


__all__ = ["Agent", "GeneralAssistant", "OSINTAgent", "ReconAgent", "ReportAgent", "build_agents"]
