"""Darknet lookup — intentionally a safe stub.

DeathBot does not crawl or proxy Tor/darknet marketplaces. This returns a clear
notice instead of pretending to. Wire an authorised, vetted feed here if needed.
"""
from __future__ import annotations


async def darknet_search(query: str) -> dict:
    return {
        "query": query.strip(),
        "available": False,
        "note": (
            "Darknet crawling is disabled by design. Connect an authorised threat "
            "feed (e.g. a vetted leak/marketplace API) to enable this safely."
        ),
    }
