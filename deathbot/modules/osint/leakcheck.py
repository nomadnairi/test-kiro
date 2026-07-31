"""Leak/breach lookup — aggregates only lawful "breach notification" sources.

This deliberately does NOT wrap "пробив"-style services (LeakOSINT and its
clones) that resell the *contents* of hacked databases (plaintext passwords,
owner-linked vehicle/phone records, etc.) to anyone who pays — trading stolen
personal data without the subjects' consent is illegal in most jurisdictions
(RU 152-FZ, EU GDPR) regardless of how access to the bot itself is restricted.

Free sources (always on, no key):
  - LeakCheck public API   — which breaches a query appeared in + which fields
                              leaked (not the values themselves).
  - Hudson Rock Cavalier   — infostealer-malware exposure: was this
                              email/username found in a stealer log, and how
                              many credentials were harvested from that machine.

Paid sources (optional, only if you hold a legitimate account+key):
  - Dehashed / LeakCheck Pro — set DEHASHED_API_KEY / LEAKCHECK_PRO_KEY in .env
    to add them to the aggregate. Left unset by default; nothing is silently
    enabled.
"""
from __future__ import annotations

import httpx

_LEAKCHECK_PUBLIC = "https://leakcheck.io/api/public"
_CAVALIER_URL = "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-login"


async def _leakcheck_public(query: str, timeout: int) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(_LEAKCHECK_PUBLIC, params={"check": query},
                                    headers={"User-Agent": "DeathBot"})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"source": "LeakCheck", "error": str(exc)}
    except ValueError:
        return {"source": "LeakCheck", "error": "некорректный ответ сервиса"}

    if not data.get("success"):
        return {"source": "LeakCheck", "found": 0}

    sources = data.get("sources", []) or []
    return {
        "source": "LeakCheck",
        "found": data.get("found", 0),
        "fields": data.get("fields", []),
        "breaches": [
            (s.get("name", "?") + (f" ({s['date']})" if s.get("date") else ""))
            for s in sources[:20]
        ],
    }


async def _hudsonrock_cavalier(query: str, timeout: int) -> dict:
    """Infostealer exposure — free, no key. Works best for emails/usernames."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(_CAVALIER_URL, params={"username": query})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"source": "Hudson Rock", "error": str(exc)}
    except ValueError:
        return {"source": "Hudson Rock", "error": "некорректный ответ сервиса"}

    stealers = data.get("stealers") or []
    if not stealers and data.get("message", "").lower().startswith("no results"):
        return {"source": "Hudson Rock", "found": 0}
    total_creds = sum(s.get("total_corporate_services", 0) + s.get("total_user_services", 0)
                      for s in stealers)
    return {
        "source": "Hudson Rock",
        "found": len(stealers),
        "infected_machines": len(stealers),
        "credentials_on_machine": total_creds or None,
        "note": "Найден в логах инфостилера — заражённое устройство. "
                "Не сама утечка сайта, а вредонос на компьютере жертвы." if stealers else None,
    }


async def _dehashed(query: str, api_key: str, timeout: int) -> dict | None:
    if not api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(
                "https://api.dehashed.com/search", params={"query": query},
                headers={"Accept": "application/json"}, auth=("api", api_key),
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"source": "Dehashed", "error": str(exc)}
    return {"source": "Dehashed", "found": data.get("total", 0),
            "entries": data.get("entries", [])[:10]}


async def leak_lookup(query: str, dehashed_key: str = "", timeout: int = 20) -> dict:
    """Aggregate every configured lawful leak-notification source."""
    q = query.strip().lstrip("@")
    if not q:
        return {"query": q, "error": "пустой запрос"}

    results = [await _leakcheck_public(q, timeout), await _hudsonrock_cavalier(q, timeout)]
    paid = await _dehashed(q, dehashed_key, timeout)
    if paid is not None:
        results.append(paid)

    total_found = sum(r.get("found") or 0 for r in results if not r.get("error"))
    return {
        "query": q,
        "total_hits": total_found,
        "sources": results,
        "note": "Бесплатные источники показывают факт/источник утечки и заражения "
                "инфостилером, но не сами пароли. Полные записи — только с "
                "платным ключом легитимного сервиса (Dehashed) в .env.",
    }
