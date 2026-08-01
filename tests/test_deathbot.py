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

import httpx

from deathbot.ai.providers.base import error_detail
from deathbot.ai.router import AIRouter
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


# --------------------------------------------------------------------------- #
# AI router: provider identity, per-provider models, local-server opt-in,
# per-user key override (the bugs reported: unreadable "openai-compatible"
# errors, shared model breaking OpenAI/Groq/DeepSeek, keys added via the bot
# UI never reaching the router)
# --------------------------------------------------------------------------- #
def test_provider_identity_is_distinct():
    router = AIRouter(load_settings())
    names = {pid: p.name for pid, p in router._providers.items()}
    assert names["openai"] == "openai"
    assert names["openrouter"] == "openrouter"
    assert names["groq"] == "groq"
    assert names["deepseek"] == "deepseek"
    assert names["grok"] == "grok"
    # No two providers should share the base class's generic name anymore.
    assert len(set(names.values())) == len(names)
    assert "openai-compatible" not in names.values()


def test_per_provider_default_models_are_not_shared():
    router = AIRouter(load_settings())
    # OpenRouter uses vendor-prefixed slugs; real OpenAI/Groq/DeepSeek APIs 404
    # on that naming, so each provider must carry its own default model.
    assert router._models["openrouter"] == "openai/gpt-4o-mini"
    assert router._models["openai"] == "gpt-4o-mini"
    assert router._models["groq"] != router._models["openrouter"]
    assert router._models["deepseek"] != router._models["openrouter"]


def test_local_servers_are_opt_in_not_guessed():
    router = AIRouter(load_settings())
    # No env var set → these must NOT be "available" just because of a
    # guessed localhost default; otherwise every chat silently wastes time
    # trying to reach a server that was never configured.
    assert router._providers["ollama"].available is False
    assert router._providers["lmstudio"].available is False
    assert router._providers["anythingllm"].available is False


def test_resolution_order_prioritises_users_own_key():
    router = AIRouter(load_settings())
    order = router._resolution_order(None, {"claude": "sk-personal"})
    assert order[0] == "claude"


def test_user_key_builds_a_fresh_correctly_named_instance():
    router = AIRouter(load_settings())
    built = router._builders["openrouter"]("sk-user-key")
    assert built.api_key == "sk-user-key"
    assert built.name == "openrouter"
    assert built is not router._providers["openrouter"]  # doesn't mutate the shared one


def test_provider_status_reflects_a_user_key_with_no_env_key():
    settings = load_settings()
    settings.ai_keys.openrouter = ""  # make sure there's no env-configured key
    router = AIRouter(settings)
    row = next(r for r in router.provider_status({"openrouter": "sk-personal"})
              if r["name"] == "openrouter")
    assert row["available"] is True
    assert row["source"] == "личный ключ"


def test_ai_service_user_keys_filters_to_ai_provider_ids_only():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            c = Container.build(s)
            await c.startup()
            await c.access.register_seen(1, "u", "U")
            await c.api_keys.set_key(1, "openrouter", "sk-or-123")
            await c.api_keys.set_key(1, "shodan", "shodan-abc")  # not an AI id
            keys = await c.ai.user_keys(1)
            await c.shutdown()
            return keys

    assert asyncio.run(scenario()) == {"openrouter": "sk-or-123"}


def test_osint_service_prefers_personal_key_over_env():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            s.osint_keys["shodan"] = "env-key"
            c = Container.build(s)
            await c.startup()
            await c.access.register_seen(1, "u", "U")
            await c.api_keys.set_key(1, "shodan", "personal-key")
            resolved = await c.osint._key(1, "shodan")
            await c.shutdown()
            return resolved

    assert asyncio.run(scenario()) == "personal-key"


def _fake_response(status: int, json_body=None, text: str = "") -> httpx.Response:
    kwargs = {"status_code": status, "request": httpx.Request("POST", "https://x/")}
    if json_body is not None:
        return httpx.Response(**kwargs, json=json_body)
    return httpx.Response(**kwargs, text=text)


def test_error_detail_extracts_vendor_message_not_bare_status():
    # OpenRouter/OpenAI-style: {"error": {"message": "...", "code": 404}}
    resp = _fake_response(404, json_body={
        "error": {"message": "No endpoints found matching your data policy", "code": 404}
    })
    assert error_detail(resp) == "No endpoints found matching your data policy"


def test_error_detail_falls_back_to_plain_text_body():
    resp = _fake_response(500, text="upstream timeout")
    assert error_detail(resp) == "upstream timeout"


def test_error_detail_never_raises_on_garbage_body():
    resp = _fake_response(400, text="<html>not json</html>")
    assert isinstance(error_detail(resp), str) and error_detail(resp)


def test_openrouter_200_with_embedded_error_is_not_a_bare_malformed_response():
    """Reproduces the reported bug: OpenRouter can answer HTTP 200 with an
    {"error": {...}} body instead of "choices" (e.g. no endpoints available
    for a :free model's data policy) — this used to surface as an opaque
    "openrouter: malformed response" with zero diagnostic value."""
    from deathbot.ai.providers.base import ChatMessage
    from deathbot.ai.providers.openai_compatible import OpenAICompatibleProvider

    async def scenario():
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={
                "error": {
                    "message": "No endpoints found matching your data policy "
                              "(Free model publication)",
                    "code": 404,
                }
            })

        provider = OpenAICompatibleProvider(
            name="openrouter", api_key="sk-test",
            base_url="https://openrouter.ai/api/v1", model="nvidia/x:free",
        )
        transport = httpx.MockTransport(handler)
        real_client = httpx.AsyncClient
        try:
            httpx.AsyncClient = lambda *a, **kw: real_client(*a, transport=transport, **kw)
            from deathbot.ai.providers.base import ProviderError
            try:
                await provider.chat([ChatMessage("user", "hi")])
                return None
            except ProviderError as exc:
                return str(exc)
        finally:
            httpx.AsyncClient = real_client

    message = asyncio.run(scenario())
    assert message is not None
    assert "No endpoints found matching your data policy" in message
    assert "malformed response" not in message
