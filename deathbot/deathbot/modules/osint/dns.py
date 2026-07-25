"""DNS lookups using the standard library resolver (no external deps)."""
from __future__ import annotations

import asyncio
import socket


async def dns_lookup(host: str) -> dict:
    """Resolve A/AAAA records and the reverse PTR for a host."""
    loop = asyncio.get_running_loop()
    result: dict = {"host": host, "addresses": [], "reverse": None, "error": None}
    try:
        infos = await loop.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        addrs = sorted({info[4][0] for info in infos})
        result["addresses"] = addrs
        if addrs:
            try:
                result["reverse"] = (await loop.getnameinfo((addrs[0], 0), 0))[0]
            except OSError:
                result["reverse"] = None
    except (socket.gaierror, OSError) as exc:
        result["error"] = str(exc)
    return result
