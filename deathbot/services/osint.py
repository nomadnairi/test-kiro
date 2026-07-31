"""OSINTService — wraps the OSINT modules with audit logging and light caching."""
from __future__ import annotations

import json

from ..config import Settings
from ..modules import osint as m
from ..repositories import Repositories


class OSINTService:
    def __init__(self, settings: Settings, repos: Repositories) -> None:
        self.settings = settings
        self.repos = repos
        self.keys = settings.osint_keys

    async def _cached(self, key: str, ttl: int, producer):
        hit = await self.repos.cache.get(key)
        if hit:
            return json.loads(hit)
        data = await producer()
        await self.repos.cache.set(key, json.dumps(data), ttl_seconds=ttl)
        return data

    async def _audit(self, user_id: int, action: str, detail: str) -> None:
        await self.repos.audit.log(user_id, action, detail)

    async def whois(self, user_id: int, domain: str) -> dict:
        await self._audit(user_id, "osint.whois", domain)
        return await self._cached(f"whois:{domain.lower()}", 3600,
                                  lambda: m.whois_lookup(domain))

    async def dns(self, user_id: int, host: str) -> dict:
        await self._audit(user_id, "osint.dns", host)
        return await m.dns_lookup(host)

    async def subdomains(self, user_id: int, domain: str) -> dict:
        await self._audit(user_id, "osint.subdomains", domain)
        return await self._cached(f"subs:{domain.lower()}", 3600,
                                  lambda: m.subdomains(domain))

    async def username(self, user_id: int, username: str) -> dict:
        await self._audit(user_id, "osint.username", username)
        return await m.username_search(username)

    async def email(self, user_id: int, email: str) -> dict:
        await self._audit(user_id, "osint.email", email)
        return await m.email_search(email, hibp_key=self.keys.get("hibp", ""))

    async def phone(self, user_id: int, number: str) -> dict:
        await self._audit(user_id, "osint.phone", number)
        return await m.phone_search(number)

    async def geoip(self, user_id: int, target: str) -> dict:
        await self._audit(user_id, "osint.geoip", target)
        return await self._cached(f"geoip:{target}", 1800, lambda: m.geoip(target))

    async def shodan(self, user_id: int, ip: str) -> dict:
        await self._audit(user_id, "osint.shodan", ip)
        return await m.shodan_host(ip, self.keys.get("shodan", ""))

    async def threat_intel(self, user_id: int, indicator: str) -> dict:
        await self._audit(user_id, "osint.threatintel", indicator)
        return await m.threat_intel(indicator, abuseipdb_key=self.keys.get("abuseipdb", ""))

    async def ioc(self, user_id: int, value: str) -> dict:
        await self._audit(user_id, "osint.ioc", value)
        return await m.classify_ioc(value)

    async def reverse_image(self, user_id: int, url: str) -> dict:
        await self._audit(user_id, "osint.reverse_image", url)
        return await m.reverse_image(url)

    async def darknet(self, user_id: int, query: str) -> dict:
        await self._audit(user_id, "osint.darknet", query)
        return await m.darknet_search(query)

    def exif(self, image_bytes: bytes) -> dict:
        return m.extract_exif(image_bytes)

    async def cli(self, user_id: int, tool_id: str, target: str) -> dict:
        """Run a real OSINT CLI tool from GitHub (installed in the image)."""
        await self._audit(user_id, f"osint.{tool_id}", target)
        return await m.run_cli_tool(tool_id, target)

    def cli_tools(self) -> dict[str, str]:
        return m.describe_cli()
