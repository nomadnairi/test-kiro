"""OSINTService — domain/host intelligence with light caching."""
from __future__ import annotations

import json

from ..config import Settings
from ..modules.osint import dns_lookup, whois_lookup
from ..repositories import Repositories


class OSINTService:
    def __init__(self, settings: Settings, repos: Repositories) -> None:
        self.settings = settings
        self.repos = repos

    async def whois(self, user_id: int, domain: str) -> dict:
        cache_key = f"whois:{domain.lower()}"
        cached = await self.repos.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        data = await whois_lookup(domain)
        await self.repos.cache.set(cache_key, json.dumps(data), ttl_seconds=3600)
        await self.repos.audit.log(user_id, "osint.whois", domain)
        return data

    async def dns(self, user_id: int, host: str) -> dict:
        data = await dns_lookup(host)
        await self.repos.audit.log(user_id, "osint.dns", host)
        return data
