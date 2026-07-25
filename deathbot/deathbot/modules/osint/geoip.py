"""IP geolocation via the free ip-api.com endpoint (no key)."""
from __future__ import annotations

import httpx


async def geoip(target: str, timeout: int = 15) -> dict:
    target = target.strip()
    fields = "status,message,query,country,regionName,city,zip,lat,lon,isp,org,as,reverse,timezone"
    url = f"http://ip-api.com/json/{target}?fields={fields}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        return {"query": target, "error": str(exc)}
    if data.get("status") != "success":
        return {"query": target, "error": data.get("message", "lookup failed")}
    if data.get("lat") is not None:
        data["map"] = f"https://www.openstreetmap.org/?mlat={data['lat']}&mlon={data['lon']}#map=12/{data['lat']}/{data['lon']}"
    return data
