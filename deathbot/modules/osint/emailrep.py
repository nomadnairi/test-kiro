"""EmailRep (emailrep.io) — email reputation lookup.

Free to use without a key (rate-limited); an optional key raises the limit.
Reports reputation signals (suspicious, malicious activity, credential leaks,
blacklists, spam) — not the leaked content itself, same "notification, not
resale" model as the leak aggregator.
"""
from __future__ import annotations

import httpx

_BASE = "https://emailrep.io"


async def reputation(email: str, api_key: str = "", timeout: int = 15) -> dict:
    headers = {"User-Agent": "DeathBot"}
    if api_key:
        headers["Key"] = api_key
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{_BASE}/{email}", headers=headers)
    except httpx.HTTPError as exc:
        return {"email": email, "available": False, "reason": str(exc)}

    if resp.status_code == 429:
        return {"email": email, "available": False,
               "reason": "лимит запросов исчерпан (добавь ключ в .env: EMAILREP_API_KEY)"}
    if resp.status_code != 200:
        return {"email": email, "available": False, "reason": f"HTTP {resp.status_code}"}

    data = resp.json()
    details = data.get("details", {})
    return {
        "email": email,
        "available": True,
        "reputation": data.get("reputation"),
        "suspicious": data.get("suspicious"),
        "references": data.get("references"),
        "blacklisted": details.get("blacklisted"),
        "malicious_activity": details.get("malicious_activity"),
        "credentials_leaked": details.get("credentials_leaked"),
        "data_breach": details.get("data_breach"),
        "spam": details.get("spam"),
        "first_seen": details.get("first_seen"),
        "last_seen": details.get("last_seen"),
    }
