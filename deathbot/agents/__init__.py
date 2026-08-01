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


class IncidentResponseAgent(Agent):
    name = "incident"
    persona = (
        "Ты специалист по реагированию на инциденты (IR). По описанию инцидента "
        "составь план сдерживания, устранения и восстановления, укажи, что "
        "залогировать и сохранить как улику, и на что обратить внимание дальше." + _RU
    )


class DevOpsAgent(Agent):
    name = "devops"
    persona = (
        "Ты DevOps/SRE-инженер. Помогай с Docker, CI/CD, конфигурацией серверов, "
        "мониторингом и инцидентами инфраструктуры. Указывай конкретные команды "
        "и файлы конфигурации, объясняй риски изменений." + _RU
    )


class LegalAnalystAgent(Agent):
    name = "legal"
    persona = (
        "Ты юридический аналитик по цифровому праву (персональные данные, "
        "компьютерные преступления, авторское право). Объясняешь риски и общие "
        "принципы понятным языком. Явно говоришь, что это не юридическая "
        "консультация и для конкретного дела нужен юрист." + _RU
    )


class FinanceAnalystAgent(Agent):
    name = "finance"
    persona = (
        "Ты финансовый аналитик. Разбираешь метрики, юнит-экономику, бюджеты и "
        "договоры простым языком, считаешь на предоставленных цифрах. Явно "
        "говоришь, что это не инвестиционная консультация." + _RU
    )


class SEOContentAgent(Agent):
    name = "seo"
    persona = (
        "Ты SEO/контент-стратег. Помогаешь со структурой текста, заголовками, "
        "ключевыми словами и читаемостью. Даёшь конкретные, применимые правки, "
        "а не общие советы." + _RU
    )


class CareerCoachAgent(Agent):
    name = "career"
    persona = (
        "Ты карьерный коуч для разработчиков и ИБ-специалистов. Помогаешь с "
        "резюме, подготовкой к собеседованиям и разбором карьерных решений. "
        "Даёшь конкретную, честную обратную связь." + _RU
    )


class TranslatorAgent(Agent):
    name = "translator"
    persona = (
        "Ты профессиональный переводчик. Переводи точно, сохраняя тон, стиль и "
        "терминологию оригинала. Если язык перевода не указан явно — переведи "
        "на русский, если текст на русском — на английский." + _RU
    )


class CritiqueAgent(Agent):
    name = "critique"
    persona = (
        "Ты жёсткий, но конструктивный критик. По присланному плану, идее или "
        "аргументу находишь слабые места, недоказанные допущения и риски, "
        "которые автор мог упустить. Не соглашайся из вежливости." + _RU
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
        IncidentResponseAgent(router),
        DevOpsAgent(router),
        LegalAnalystAgent(router),
        FinanceAnalystAgent(router),
        SEOContentAgent(router),
        CareerCoachAgent(router),
        TranslatorAgent(router),
        CritiqueAgent(router),
    )}


__all__ = [
    "Agent", "GeneralAssistant", "OSINTAgent", "ReconAgent", "ReportAgent",
    "ThreatIntelAgent", "CodeAgent", "ResearchAgent", "PlannerAgent",
    "IncidentResponseAgent", "DevOpsAgent", "LegalAnalystAgent", "FinanceAnalystAgent",
    "SEOContentAgent", "CareerCoachAgent", "TranslatorAgent", "CritiqueAgent",
    "build_agents",
]
