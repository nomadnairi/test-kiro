"""Subdomain enumeration via the free crt.sh certificate-transparency log."""
from __future__ import annotations

import httpx


async def subdomains(domain: str, timeout: int = 30) -> dict:
    domain = domain.strip().lower().lstrip("*.")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "DeathBot"})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"domain": domain, "error": str(exc), "subdomains": []}
    except ValueError:
        return {"domain": domain, "error": "crt.sh returned no JSON", "subdomains": []}

    found: set[str] = set()
    for row in data:
        for name in str(row.get("name_value", "")).splitlines():
            name = name.strip().lstrip("*.").lower()
            if name.endswith(domain):
                found.add(name)
    return {"domain": domain, "count": len(found), "subdomains": sorted(found)}
