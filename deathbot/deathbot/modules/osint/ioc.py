"""IOC classification — detect the indicator type and suggest lookups."""
from __future__ import annotations

import re

_PATTERNS = [
    ("ipv4", re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")),
    ("md5", re.compile(r"^[a-fA-F0-9]{32}$")),
    ("sha1", re.compile(r"^[a-fA-F0-9]{40}$")),
    ("sha256", re.compile(r"^[a-fA-F0-9]{64}$")),
    ("cve", re.compile(r"^CVE-\d{4}-\d{4,7}$", re.I)),
    ("email", re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")),
    ("url", re.compile(r"^https?://", re.I)),
    ("domain", re.compile(r"^(?=.{1,253}$)([a-z0-9-]+\.)+[a-z]{2,}$", re.I)),
]

_SUGGESTIONS = {
    "ipv4": ["geoip", "threat_intel", "shodan"],
    "domain": ["whois", "dns", "subdomains", "threat_intel"],
    "url": ["threat_intel"],
    "email": ["email"],
    "md5": ["threat_intel"],
    "sha1": ["threat_intel"],
    "sha256": ["threat_intel"],
    "cve": ["ai (explain CVE)"],
}


async def classify_ioc(value: str) -> dict:
    value = value.strip()
    ioc_type = "unknown"
    for name, pat in _PATTERNS:
        if pat.match(value):
            ioc_type = name
            break
    return {
        "value": value,
        "type": ioc_type,
        "suggested_lookups": _SUGGESTIONS.get(ioc_type, []),
    }
