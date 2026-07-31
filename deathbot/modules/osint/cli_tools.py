"""Wrappers around real OSINT CLIs from GitHub, run through the shared runner.

Each tool declares its binary, how to build argv from a single target, a timeout
and a short human description. If the binary is not installed the wrapper says so
cleanly instead of failing, so the bot works everywhere and every tool becomes
fully functional wherever it is installed. Tools that write files run in /tmp
(the container's /app is read-only).

For authorised / lawful use only.
"""
from __future__ import annotations

from collections.abc import Callable

from ...util import run_command

_TMP = "/tmp"

# id -> (binary, argv(target) -> list[str], timeout, human description)
TOOLS: dict[str, tuple[str, Callable[[str], list[str]], int, str]] = {
    "theharvester": (
        "theHarvester",
        lambda t: ["theHarvester", "-d", t, "-b", "bing,duckduckgo,crtsh,otx", "-l", "100"],
        300, "Сбор email, поддоменов и хостов из открытых источников"),
    "sherlock_cli": (
        "sherlock",
        lambda t: ["sherlock", t, "--timeout", "10", "--print-found", "--no-color"],
        180, "Поиск юзернейма по сотням соцсетей и сайтов"),
    "holehe": (
        "holehe",
        lambda t: ["holehe", t, "--only-used", "--no-color"],
        150, "Где зарегистрирован email (по функции восстановления пароля)"),
    "maigret": (
        "maigret",
        lambda t: ["maigret", t, "--timeout", "10", "--top-sites", "50",
                   "--no-color", "--no-recursion"],
        300, "Юзернейм на 2500+ сайтах + данные из профилей"),
    "socialscan": (
        "socialscan",
        lambda t: ["socialscan", t],
        120, "Занятость email/username на популярных платформах"),
    "h8mail": (
        "h8mail",
        lambda t: ["h8mail", "-t", t, "--loose"],
        150, "Поиск email в публичных утечках и дампах"),
    "dnstwist": (
        "dnstwist",
        lambda t: ["dnstwist", "-r", "--format", "cli", t],
        180, "Домены-двойники: тайпсквоттинг и фишинг"),
    "dnsrecon": (
        "dnsrecon",
        lambda t: ["dnsrecon", "-d", t],
        150, "Перечисление DNS-записей, зон и поддоменов"),
    "sublist3r": (
        "sublist3r",
        lambda t: ["sublist3r", "-n", "-d", t],
        180, "Поиск поддоменов через поисковые системы"),
    "checkdmarc": (
        "checkdmarc",
        lambda t: ["checkdmarc", t],
        90, "Почтовая защита домена: SPF / DKIM / DMARC"),
    "wafw00f": (
        "wafw00f",
        lambda t: ["wafw00f", t],
        90, "Определение WAF / файрвола перед сайтом"),
    "metafinder": (
        "metafinder",
        lambda t: ["metafinder", "-d", t, "-l", "15", "-o", f"{_TMP}/metafinder", "-go"],
        240, "Метаданные (авторы, софт) из публичных документов домена"),
    "whatweb": (
        "whatweb",
        lambda t: ["whatweb", "--no-errors", "-a", "1", t],
        120, "Фингерпринт технологий, CMS и заголовков сайта"),
    "gau": (
        "gau",
        lambda t: ["gau", "--subs", t],
        150, "Все известные URL домена (Wayback, OTX, CommonCrawl)"),
    "phoneinfoga": (
        "phoneinfoga",
        lambda t: ["phoneinfoga", "scan", "-n", t],
        120, "OSINT по номеру телефона: оператор, тип, следы в сети"),
}


def describe() -> dict[str, str]:
    return {tid: meta[3] for tid, meta in TOOLS.items()}


async def run_tool(tool_id: str, target: str) -> dict:
    meta = TOOLS.get(tool_id)
    if meta is None:
        return {"tool": tool_id, "error": "неизвестный инструмент"}
    binary, build, timeout, desc = meta
    result = await run_command(build(target.strip()), timeout=timeout, cwd=_TMP)
    if result.missing:
        return {
            "tool": tool_id, "target": target, "installed": False,
            "hint": f"`{binary}` не установлен на хосте. {desc}.",
        }
    return {
        "tool": tool_id, "target": target, "installed": True,
        "ok": result.ok,
        "output": (result.stdout or result.stderr).strip() or "(пустой вывод)",
    }
