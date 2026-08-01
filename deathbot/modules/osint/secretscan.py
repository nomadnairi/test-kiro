"""Secret scanner — regex detector for leaked API keys/tokens in pasted text.

Runs fully offline: no network calls, no third-party service, nothing sent
anywhere. Patterns match the public, vendor-documented *shape* of common API
keys/tokens (the same kind of signatures open-source scanners like gitleaks
or trufflehog ship by default) — this file does not know or store any real
secret, it only recognises formats.

Matches are masked before being shown back (never echo a full key to chat),
and the caller must never pass the raw scanned text into the audit log —
only its length.
"""
from __future__ import annotations

import re

# (service label, confidence, pattern). Vendor-prefixed patterns are
# near-unambiguous ("high"); patterns that rely on a nearby keyword
# (`api_key = "..."`) are more prone to false positives ("low"/"medium").
_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("AWS Access Key ID", "high", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("AWS Secret Access Key", "medium",
     re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?")),
    ("GitHub PAT (classic)", "high", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("GitHub PAT (fine-grained)", "high", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("GitHub OAuth token", "high", re.compile(r"\bgho_[A-Za-z0-9]{36}\b")),
    ("GitLab PAT", "high", re.compile(r"\bglpat-[A-Za-z0-9\-_]{20}\b")),
    ("Slack token", "high", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,48}\b")),
    ("Slack webhook URL", "high", re.compile(
        r"https://hooks\.slack\.com/services/T[A-Za-z0-9]{8,10}/B[A-Za-z0-9]{8,10}/[A-Za-z0-9]{24}")),
    ("Stripe live secret key", "high", re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b")),
    ("Stripe test secret key", "high", re.compile(r"\bsk_test_[A-Za-z0-9]{24,}\b")),
    ("Stripe publishable key", "medium", re.compile(r"\bpk_live_[A-Za-z0-9]{24,}\b")),
    ("SendGrid API key", "high", re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b")),
    ("Mailgun API key", "high", re.compile(r"\bkey-[a-f0-9]{32}\b")),
    ("Twilio Account SID", "medium", re.compile(r"\bAC[a-f0-9]{32}\b")),
    ("OpenAI API key (legacy)", "high",
     re.compile(r"\bsk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}\b")),
    ("OpenAI API key (project)", "high", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b")),
    ("Anthropic API key", "high", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{90,}\b")),
    ("Hugging Face token", "high", re.compile(r"\bhf_[A-Za-z0-9]{34,}\b")),
    ("npm token", "high", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("PyPI token", "high", re.compile(r"\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{20,}\b")),
    ("Docker Hub PAT", "high", re.compile(r"\bdckr_pat_[A-Za-z0-9_-]{27,}\b")),
    ("Google API key", "high", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Firebase project URL", "low", re.compile(r"\b[a-z0-9-]+\.firebaseio\.com\b")),
    ("JWT", "medium", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("RSA private key", "high", re.compile(r"-----BEGIN RSA PRIVATE KEY-----")),
    ("EC private key", "high", re.compile(r"-----BEGIN EC PRIVATE KEY-----")),
    ("OpenSSH private key", "high", re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----")),
    ("PGP private key", "high", re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----")),
    ("Generic private key", "high", re.compile(r"-----BEGIN PRIVATE KEY-----")),
    ("Discord bot token", "medium",
     re.compile(r"\b[MN][A-Za-z0-9_-]{23,25}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{25,40}\b")),
    ("Telegram bot token", "high", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("DigitalOcean PAT", "high", re.compile(r"\bdop_v1_[a-f0-9]{64}\b")),
    ("New Relic API key", "high", re.compile(r"\bNRAK-[A-Z0-9]{27}\b")),
    ("Sentry DSN", "high", re.compile(r"https://[a-f0-9]{32}@[a-z0-9.\-]+\.ingest\.sentry\.io/\d+")),
    ("Basic auth in URL", "medium", re.compile(r"[a-zA-Z][a-zA-Z0-9+.\-]*://[^\s:@/]+:[^\s:@/]+@")),
    ("Bearer token in header", "low",
     re.compile(r"(?i)Authorization:\s*Bearer\s+([A-Za-z0-9_\-.]{20,})")),
    ("Generic API key assignment", "low",
     re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*['\"]([A-Za-z0-9_\-]{16,})['\"]")),
    ("Generic secret/token assignment", "low",
     re.compile(r"(?i)\b(?:secret|token|access[_-]?key)\s*[:=]\s*['\"]([A-Za-z0-9_\-/+=]{16,})['\"]")),
]

_CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "…"
    if len(value) <= 10:
        return f"{value[:2]}…{value[-2:]}"
    return f"{value[:6]}…{value[-4:]}"


def scan_text(text: str) -> dict:
    """Find likely secrets in ``text``. Pure regex, offline, no side effects."""
    findings = []
    seen: set[tuple[str, str]] = set()
    for service, confidence, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            value = m.group(1) if m.groups() else m.group(0)
            key = (service, value)
            if key in seen:
                continue
            seen.add(key)
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append({
                "service": service,
                "confidence": confidence,
                "match": _mask(value),
                "line": line_no,
            })
    findings.sort(key=lambda f: _CONFIDENCE_ORDER[f["confidence"]])
    return {
        "chars_scanned": len(text),
        "count": len(findings),
        "findings": findings[:60],
    }
