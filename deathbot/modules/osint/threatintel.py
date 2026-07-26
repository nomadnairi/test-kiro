"""Threat intelligence: URLhaus (free) for URLs/hosts, AbuseIPDB (key) for IPs."""
from __future__ import annotations

import httpx


async def _urlhaus(host: str, timeout: int) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                "https://urlhaus-api.abuse.ch/v1/host/", data={"host": host}
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"source": "urlhaus", "error": str(exc)}
    if data.get("query_status") == "no_results":
        return {"source": "urlhaus", "listed": False}
    return {
        "source": "urlhaus",
        "listed": data.get("query_status") == "ok",
        "url_count": data.get("url_count"),
        "urls": [u.get("url") for u in (data.get("urls") or [])[:5]],
    }


async def _abuseipdb(ip: str, api_key: str, timeout: int) -> dict:
    if not api_key:
        return {"source": "abuseipdb", "available": False, "reason": "no API key"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(
                "https://api.abuseipdb.com/api/v2/check",
                params={"ipAddress": ip, "maxAgeInDays": 90},
                headers={"Key": api_key, "Accept": "application/json"},
            )
            resp.raise_for_status()
            d = resp.json().get("data", {})
    except httpx.HTTPError as exc:
        return {"source": "abuseipdb", "available": False, "reason": str(exc)}
    return {
        "source": "abuseipdb",
        "available": True,
        "abuse_score": d.get("abuseConfidenceScore"),
        "total_reports": d.get("totalReports"),
        "country": d.get("countryCode"),
        "isp": d.get("isp"),
    }


async def threat_intel(indicator: str, abuseipdb_key: str = "", timeout: int = 20) -> dict:
    indicator = indicator.strip()
    is_ip = indicator.replace(".", "").isdigit() and indicator.count(".") == 3
    result: dict = {"indicator": indicator, "sources": []}
    result["sources"].append(await _urlhaus(indicator, timeout))
    if is_ip:
        result["sources"].append(await _abuseipdb(indicator, abuseipdb_key, timeout))
    return result
