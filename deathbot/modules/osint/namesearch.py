"""Search by full name (ФИО) — build ready-to-open search-engine / social dorks.

There's no reliable free "name → data" API, so the practical OSINT move is to
hand the name to the engines and people-search sites. This returns clickable
queries (exact-match where supported).
"""
from __future__ import annotations

from urllib.parse import quote


async def name_search(name: str) -> dict:
    n = name.strip()
    q = quote(n)
    exact = quote(f'"{n}"')
    return {
        "name": n,
        "engines": {
            "Google": f"https://www.google.com/search?q={exact}",
            "Yandex": f"https://yandex.ru/search/?text={exact}",
            "Bing": f"https://www.bing.com/search?q={exact}",
            "VK": f"https://vk.com/search?c[q]={q}&c[section]=people",
            "OK": f"https://ok.ru/search?st.query={q}",
            "Facebook": f"https://www.facebook.com/search/people/?q={q}",
            "LinkedIn": f"https://www.linkedin.com/search/results/people/?keywords={q}",
            "Telegram": f"https://t.me/s/?q={q}",
        },
        "note": "Открытые ссылки для ручной проверки — сузь по городу/возрасту/фото.",
    }
