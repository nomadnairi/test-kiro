"""Username presence check across popular sites (sherlock-style, no API key).

Sends a lightweight HEAD/GET to each profile URL and infers existence from the
HTTP status. Best-effort — some sites soft-404 with 200; treated as heuristic.
"""
from __future__ import annotations

import asyncio

import httpx

# site -> profile URL template
SITES: dict[str, str] = {
    "GitHub": "https://github.com/{u}",
    "GitLab": "https://gitlab.com/{u}",
    "Twitter/X": "https://x.com/{u}",
    "Instagram": "https://www.instagram.com/{u}/",
    "Reddit": "https://www.reddit.com/user/{u}",
    "Telegram": "https://t.me/{u}",
    "TikTok": "https://www.tiktok.com/@{u}",
    "Twitch": "https://www.twitch.tv/{u}",
    "Medium": "https://medium.com/@{u}",
    "Keybase": "https://keybase.io/{u}",
    "HackerNews": "https://news.ycombinator.com/user?id={u}",
    "Steam": "https://steamcommunity.com/id/{u}",
}


async def _check(client: httpx.AsyncClient, site: str, url: str) -> tuple[str, bool, str]:
    try:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 DeathBot"})
        return site, resp.status_code == 200, url
    except httpx.HTTPError:
        return site, False, url


async def username_search(username: str, timeout: int = 15) -> dict:
    username = username.strip().lstrip("@")
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(_check(client, s, u.format(u=username)) for s, u in SITES.items())
        )
    found = [{"site": s, "url": url} for s, ok, url in results if ok]
    return {"username": username, "found_count": len(found), "found": found,
            "checked": len(SITES)}
