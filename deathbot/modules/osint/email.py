"""Email intelligence: format check, Gravatar presence, and HIBP breaches."""
from __future__ import annotations

import hashlib
import re

import httpx

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


async def _gravatar(email: str, timeout: int) -> bool:
    digest = hashlib.md5(email.strip().lower().encode()).hexdigest()  # noqa: S324
    url = f"https://www.gravatar.com/avatar/{digest}?d=404"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            return (await client.get(url)).status_code == 200
    except httpx.HTTPError:
        return False


async def _hibp(email: str, api_key: str, timeout: int) -> dict:
    if not api_key:
        return {"available": False, "reason": "no HIBP API key configured"}
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
    headers = {"hibp-api-key": api_key, "User-Agent": "DeathBot"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
    except httpx.HTTPError as exc:
        return {"available": False, "reason": str(exc)}
    if resp.status_code == 404:
        return {"available": True, "breaches": []}
    if resp.status_code == 200:
        return {"available": True, "breaches": [b["Name"] for b in resp.json()]}
    return {"available": False, "reason": f"HIBP HTTP {resp.status_code}"}


async def email_search(email: str, hibp_key: str = "", timeout: int = 15) -> dict:
    email = email.strip()
    valid = bool(_EMAIL_RE.match(email))
    result: dict = {"email": email, "valid_format": valid}
    if not valid:
        return result
    result["gravatar"] = await _gravatar(email, timeout)
    result["hibp"] = await _hibp(email, hibp_key, timeout)
    return result
