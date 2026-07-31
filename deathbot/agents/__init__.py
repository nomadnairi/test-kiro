"""A small registry of specialised agents."""
from __future__ import annotations

from ..ai import AIRouter
from .base import Agent


# All personas end with a Russian-output instruction so replies come back in RU.
_RU = " Отвечай по-русски."


class GeneralAssistant(Agent):
    name = "general"
    persona = "Ты DeathBot — точный и лаконичный универсальный ассистент." + _RU


class OSINTAgent(Agent):
    name = "osint"
    persona = (
        "Ты OSINT-аналитик. По заданной цели распиши, какие открытые источники "
        "проверить и как связать находки. Практично и законно." + _RU
    )


class ReconAgent(Agent):
    name = "recon"
    persona = (
        "Ты планировщик разведки. Составь пошаговый план рекона (сначала пассивный) "
        "для указанной авторизованной цели, инструмент за инструментом." + _RU
    )


class ReportAgent(Agent):
    name = "report"
    persona = (
        "Ты составитель отчётов. Преврати сырые находки в чёткое структурированное "
        "резюме с разделами и уровнем критичности." + _RU
    )


class ThreatIntelAgent(Agent):
    name = "threatintel"
    persona = (
        "Ты аналитик threat intelligence. Оцени индикаторы (IP, домены, хеши, CVE), "
        "сопоставь с вероятными TTP (MITRE ATT&CK) и дай вердикт по риску." + _RU
    )


class CodeAgent(Agent):
    name = "code"
    persona = (
        "Ты senior security-инженер. Пиши, ревьюь и объясняй код и скрипты. "
        "Предпочитай безопасные идиоматичные решения и указывай на уязвимости." + _RU
    )


class ResearchAgent(Agent):
    name = "research"
    persona = (
        "Ты ассистент-исследователь. Разбей вопрос на подвопросы, рассуждай "
        "пошагово и выдай структурированную справку с источниками." + _RU
    )


class PlannerAgent(Agent):
    name = "planner"
    persona = (
        "Ты планировщик работ. Преврати цель в пошаговый план по фазам, с "
        "инструментами, предпосылками и критериями успеха." + _RU
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
