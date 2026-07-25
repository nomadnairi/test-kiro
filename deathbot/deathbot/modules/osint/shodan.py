"""Shodan host lookup (requires an API key)."""
from __future__ import annotations

import httpx


async def shodan_host(ip: str, api_key: str, timeout: int = 20) -> dict:
    if not api_key:
        return {"ip": ip, "available": False, "reason": "no Shodan API key configured"}
    url = f"https://api.shodan.io/shodan/host/{ip.strip()}?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
    except httpx.HTTPError as exc:
        return {"ip": ip, "available": False, "reason": str(exc)}
    if resp.status_code == 404:
        return {"ip": ip, "available": True, "found": False}
    if resp.status_code != 200:
        return {"ip": ip, "available": False, "reason": f"HTTP {resp.status_code}"}
    data = resp.json()
    return {
        "ip": ip,
        "available": True,
        "found": True,
        "org": data.get("org"),
        "os": data.get("os"),
        "isp": data.get("isp"),
        "country": data.get("country_name"),
        "ports": data.get("ports", []),
        "hostnames": data.get("hostnames", []),
        "vulns": list(data.get("vulns", []))[:20],
    }
