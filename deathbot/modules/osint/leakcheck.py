"""Leak/breach lookup via the free LeakCheck public API.

Works for an email, username, phone or hash. The public endpoint returns *where*
the query was seen (breach sources + which fields leaked), not the raw
passwords — that's what a free source can lawfully give. For full leaked records
(plaintext, phone-from-email pivots…) a paid API key (LeakCheck Pro, Dehashed,
Snusbase) is required; wire it in via env when you have one.
"""
from __future__ import annotations

import httpx

_PUBLIC = "https://leakcheck.io/api/public"


async def leak_lookup(query: str, timeout: int = 20) -> dict:
    q = query.strip().lstrip("@")
    if not q:
        return {"query": q, "error": "пустой запрос"}
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(_PUBLIC, params={"check": q},
                                    headers={"User-Agent": "DeathBot"})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"query": q, "error": str(exc)}
    except ValueError:
        return {"query": q, "error": "некорректный ответ сервиса"}

    if not data.get("success"):
        # API says "Not found" via success=false with an error string.
        return {"query": q, "found": 0, "note": data.get("error", "в утечках не найдено")}

    sources = data.get("sources", []) or []
    return {
        "query": q,
        "found": data.get("found", 0),
        "fields": data.get("fields", []),
        "sources": [
            (s.get("name", "?") + (f" ({s['date']})" if s.get("date") else ""))
            for s in sources[:25]
        ],
        "note": "Публичный источник показывает факт и источники утечки, но не сами пароли. "
                "Полные записи — только с платным ключом (LeakCheck Pro / Dehashed).",
    }
