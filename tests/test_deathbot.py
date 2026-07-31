"""Unit tests for DeathBot's pure logic (no network, no Telegram).

Async pieces use asyncio.run() so the suite needs only pytest itself.
Run: pytest -q
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deathbot.config import load_settings
from deathbot.container import Container
from deathbot.core.security import Crypto
from deathbot.modules.osint.ioc import classify_ioc
from deathbot.modules.osint.phone import phone_search
from deathbot.registry import TOOLS, human, strip_html, tools_in
from deathbot.services.export import ExportService
from deathbot.util import validate_input


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_domain():
    assert validate_input("domain", "example.com") is None
    assert validate_input("domain", "sub.example.co.uk") is None
    assert validate_input("domain", "https://example.com/path") is None
    assert validate_input("domain", "not a domain!") is not None
    assert validate_input("domain", "") is not None


def test_validate_email_ip_phone_username():
    assert validate_input("email", "user@example.com") is None
    assert validate_input("email", "nope") is not None
    assert validate_input("ip", "8.8.8.8") is None
    assert validate_input("ip", "999.1.1.1") is not None
    assert validate_input("phone", "+79161234567") is None
    assert validate_input("phone", "abc") is not None
    assert validate_input("username", "@torvalds") is None
    assert validate_input("host", "8.8.8.8") is None
    assert validate_input("host", "example.com") is None


# --------------------------------------------------------------------------- #
# crypto
# --------------------------------------------------------------------------- #
def test_crypto_roundtrip(tmp_path):
    crypto = Crypto.from_settings("", tmp_path / ".key")
    token = crypto.encrypt("sk-secret", aad=b"42:openai")
    assert crypto.decrypt(token, aad=b"42:openai") == "sk-secret"


def test_crypto_wrong_aad_fails(tmp_path):
    crypto = Crypto.from_settings("", tmp_path / ".key")
    token = crypto.encrypt("x", aad=b"a")
    import pytest
    with pytest.raises(Exception):
        crypto.decrypt(token, aad=b"b")


# --------------------------------------------------------------------------- #
# osint pure logic
# --------------------------------------------------------------------------- #
def test_ioc_classify():
    assert asyncio.run(classify_ioc("8.8.8.8"))["type"] == "ipv4"
    assert asyncio.run(classify_ioc("d41d8cd98f00b204e9800998ecf8427e"))["type"] == "md5"
    assert asyncio.run(classify_ioc("CVE-2021-44228"))["type"] == "cve"
    assert asyncio.run(classify_ioc("example.com"))["type"] == "domain"


def test_phone_parse():
    r = asyncio.run(phone_search("+79161234567"))
    assert r["country_guess"] == "Russia/Kazakhstan"
    assert r["e164"] == "+79161234567"


# --------------------------------------------------------------------------- #
# export
# --------------------------------------------------------------------------- #
def test_export_all_formats():
    ex = ExportService()
    report = {"title": "T", "generated_at": "now", "tags": ["deathbot"],
              "sections": {"a": "hello"}}
    for fmt in ("json", "markdown", "obsidian", "html", "csv", "txt", "pdf", "docx"):
        blob = ex.render(report, fmt)
        assert isinstance(blob, bytes) and len(blob) > 0
    assert ex.render(report, "pdf")[:5] == b"%PDF-"
    assert ex.render(report, "obsidian").startswith(b"---")


def test_strip_html():
    assert strip_html("<b>hi</b> &amp; bye") == "hi & bye"


# --------------------------------------------------------------------------- #
# registry integrity
# --------------------------------------------------------------------------- #
def test_registry_integrity():
    assert len(TOOLS) >= 78
    for t in TOOLS.values():
        if t.kind in ("input", "instant"):
            assert t.run is not None, f"{t.id} has no run()"
        assert t.desc, f"{t.id} has no description"
    # combines exist and are background
    combines = tools_in("workflows")
    assert len(combines) >= 3
    assert all(t.background for t in combines)


def test_human_formatter():
    out = human("Title", {"домен": "example.com", "порты": [80, 443], "raw": "x\ny"})
    assert "<b>Title</b>" in out
    assert "example.com" in out
    assert "<pre>" in out  # raw goes into a preformatted block


# --------------------------------------------------------------------------- #
# access control (async, via asyncio.run)
# --------------------------------------------------------------------------- #
def test_access_control_and_whitelist():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            s.owner_id = 1
            s.raw.setdefault("bot", {})["whitelist_only"] = True
            c = Container.build(s)
            await c.startup()
            # owner is auto-active and passes admin
            assert await c.access.register_seen(1, "o", "O") == "owner"
            assert (await c.access.check(1, "admin")).allowed
            # new guest is pending → blocked
            await c.access.register_seen(2, "g", "G")
            assert not (await c.access.check(2, "osint")).allowed
            # grant activates + authorises
            await c.access.grant(1, 2, "analyst")
            assert (await c.access.check(2, "osint")).allowed
            await c.shutdown()

    asyncio.run(scenario())


def test_db_snapshot_is_valid_sqlite():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            c = Container.build(s)
            await c.startup()
            data = await c.db.snapshot()
            await c.shutdown()
            return data

    data = asyncio.run(scenario())
    assert data[:16] == b"SQLite format 3\x00"
