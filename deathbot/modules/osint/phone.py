"""Lightweight phone-number analysis (no external service).

Parses E.164-ish input, maps the country calling code to a country, and returns
normalised digits. For deep validation, plug in `phonenumbers` later.
"""
from __future__ import annotations

import re

# A compact calling-code → country map (most common ones).
_CC = {
    "1": "US/Canada", "7": "Russia/Kazakhstan", "20": "Egypt", "27": "South Africa",
    "30": "Greece", "31": "Netherlands", "32": "Belgium", "33": "France",
    "34": "Spain", "39": "Italy", "40": "Romania", "41": "Switzerland",
    "44": "United Kingdom", "45": "Denmark", "46": "Sweden", "48": "Poland",
    "49": "Germany", "52": "Mexico", "55": "Brazil", "61": "Australia",
    "62": "Indonesia", "63": "Philippines", "64": "New Zealand", "65": "Singapore",
    "81": "Japan", "82": "South Korea", "84": "Vietnam", "86": "China",
    "90": "Turkey", "91": "India", "92": "Pakistan", "93": "Afghanistan",
    "94": "Sri Lanka", "98": "Iran", "212": "Morocco", "213": "Algeria",
    "234": "Nigeria", "254": "Kenya", "351": "Portugal", "353": "Ireland",
    "358": "Finland", "359": "Bulgaria", "370": "Lithuania", "371": "Latvia",
    "372": "Estonia", "380": "Ukraine", "420": "Czechia", "421": "Slovakia",
    "971": "UAE", "972": "Israel", "994": "Azerbaijan", "995": "Georgia",
    "998": "Uzbekistan",
}


async def phone_search(number: str) -> dict:
    raw = number.strip()
    digits = re.sub(r"[^\d]", "", raw)
    has_plus = raw.strip().startswith("+")
    country = None
    if has_plus or digits:
        for length in (3, 2, 1):
            code = digits[:length]
            if code in _CC:
                country = _CC[code]
                break
    return {
        "input": raw,
        "digits": digits,
        "e164": f"+{digits}" if digits else None,
        "country_guess": country,
        "length": len(digits),
        "note": "Heuristic parse. Install `phonenumbers` for carrier/line-type detail.",
    }
