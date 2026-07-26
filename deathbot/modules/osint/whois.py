"""WHOIS lookups.

Prefers the system ``whois`` binary; falls back to a raw TCP query against
whois.iana.org (which returns a referral) when the binary is unavailable.
"""
from __future__ import annotations

import asyncio

from ...util import has_binary, run_command


async def _whois_tcp(domain: str, server: str = "whois.iana.org", timeout: int = 15) -> str:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(server, 43), timeout=timeout
        )
    except (OSError, asyncio.TimeoutError) as exc:
        return f"error: {exc}"
    try:
        writer.write(f"{domain}\r\n".encode())
        await writer.drain()
        data = await asyncio.wait_for(reader.read(-1), timeout=timeout)
        return data.decode(errors="replace")
    except (OSError, asyncio.TimeoutError) as exc:
        return f"error: {exc}"
    finally:
        writer.close()


async def whois_lookup(domain: str) -> dict:
    domain = domain.strip().lower()
    if has_binary("whois"):
        res = await run_command(["whois", domain], timeout=30)
        raw = res.stdout or res.stderr
        return {"domain": domain, "source": "binary", "raw": raw}
    raw = await _whois_tcp(domain)
    return {"domain": domain, "source": "iana-tcp", "raw": raw}
