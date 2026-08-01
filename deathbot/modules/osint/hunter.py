"""Hunter.io — email finder / verifier (legitimate SaaS, requires an API key).

https://hunter.io/api-documentation — used here for domain-search (find email
patterns/known addresses for a company domain) and email-verifier (deliverability
+ confidence score for a specific address).
"""
from __future__ import annotations

import httpx

_BASE = "https://api.hunter.io/v2"


async def domain_search(domain: str, api_key: str, timeout: int = 20) -> dict:
    if not api_key:
        return {"domain": domain, "available": False, "reason": "нет ключа Hunter.io"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{_BASE}/domain-search",
                                    params={"domain": domain, "api_key": api_key})
    except httpx.HTTPError as exc:
        return {"domain": domain, "available": False, "reason": str(exc)}
    if resp.status_code != 200:
        return {"domain": domain, "available": False, "reason": f"HTTP {resp.status_code}"}

    data = resp.json().get("data", {})
    emails = [
        {"email": e.get("value"), "type": e.get("type"), "confidence": e.get("confidence")}
        for e in data.get("emails", [])[:20]
    ]
    return {
        "domain": domain,
        "available": True,
        "pattern": data.get("pattern"),
        "organization": data.get("organization"),
        "email_count": len(data.get("emails", [])),
        "emails": emails,
    }


async def verify_email(email: str, api_key: str, timeout: int = 20) -> dict:
    if not api_key:
        return {"email": email, "available": False, "reason": "нет ключа Hunter.io"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{_BASE}/email-verifier",
                                    params={"email": email, "api_key": api_key})
    except httpx.HTTPError as exc:
        return {"email": email, "available": False, "reason": str(exc)}
    if resp.status_code != 200:
        return {"email": email, "available": False, "reason": f"HTTP {resp.status_code}"}

    data = resp.json().get("data", {})
    return {
        "email": email,
        "available": True,
        "status": data.get("status"),
        "score": data.get("score"),
        "deliverable": data.get("result"),
        "disposable": data.get("disposable"),
        "webmail": data.get("webmail"),
        "mx_records": data.get("mx_records"),
    }
