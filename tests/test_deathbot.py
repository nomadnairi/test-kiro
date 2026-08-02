"""Unit tests for DeathBot's pure logic (no network, no Telegram).

Async pieces use asyncio.run() so the suite needs only pytest itself.
Run: pytest -q
"""
from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

import deathbot.modules.osint.trufflehog as trufflehog_mod
import deathbot.services.plugins as plugins_mod
from deathbot.ai.providers.base import error_detail
from deathbot.ai.router import AIRouter
from deathbot.config import load_settings
from deathbot.container import Container
from deathbot.core.security import Crypto
from deathbot.modules.osint.ioc import classify_ioc
from deathbot.modules.osint.phone import phone_search
from deathbot.mdconvert import md_to_html
from deathbot.modules.osint.secretscan import scan_text
from deathbot.modules.osint.trufflehog import scan as trufflehog_scan
from deathbot.registry import TOOLS, human, strip_html, tools_in
from deathbot.services.export import ExportService
from deathbot.util import CommandResult, validate_input


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


def test_secretscan_finds_known_key_formats():
    text = (
        "AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'\n"
        "gh_token = ghp_" + "a" * 36 + "\n"
        "clean line, nothing here\n"
    )
    r = scan_text(text)
    services = {f["service"] for f in r["findings"]}
    assert "AWS Access Key ID" in services
    assert "GitHub PAT (classic)" in services
    assert r["count"] == 2
    assert r["chars_scanned"] == len(text)


def test_secretscan_masks_matches_never_echoes_full_secret():
    secret = "ghp_" + "b" * 36
    r = scan_text(f"token: {secret}")
    assert r["count"] == 1
    assert secret not in r["findings"][0]["match"]
    assert r["findings"][0]["match"].startswith("ghp_bb")


# --------------------------------------------------------------------------- #
# markdown -> Telegram HTML (raw LLM output must never leak "**"/"##"/"|" as
# literal text, and must never produce unbalanced tags that break sendMessage)
# --------------------------------------------------------------------------- #
def _assert_balanced_tags(html: str) -> None:
    import re as _re
    for tag in ("b", "i", "code", "pre"):
        opens = len(_re.findall(f"<{tag}>", html))
        closes = len(_re.findall(f"</{tag}>", html))
        assert opens == closes, (tag, html)


def test_md_bold_and_italic_become_real_tags():
    out = md_to_html("this is **bold** and this is *italic*")
    assert out == "this is <b>bold</b> and this is <i>italic</i>"
    _assert_balanced_tags(out)


def test_md_headers_become_bold_not_literal_hashes():
    out = md_to_html("## Section title\ntext below")
    assert "##" not in out
    assert "<b>Section title</b>" in out
    _assert_balanced_tags(out)


def test_md_table_becomes_readable_bullets_not_pipe_soup():
    out = md_to_html("| A | B |\n|---|---|\n| x | y |")
    assert "|" not in out
    assert "---" not in out
    assert "• A — B" in out
    assert "• x — y" in out


def test_md_fenced_code_becomes_pre_block():
    out = md_to_html("before\n```bash\nwhois 1.2.3.4\n```\nafter")
    assert "<pre>whois 1.2.3.4</pre>" in out
    assert "```" not in out
    _assert_balanced_tags(out)


def test_md_unclosed_delimiter_never_produces_broken_html():
    # This is the failure mode that matters most: an unmatched ** must not
    # turn into an unclosed <b> that makes Telegram reject the whole message.
    out = md_to_html("some text **never closed")
    assert "<b>" not in out
    _assert_balanced_tags(out)


def test_md_html_special_chars_are_escaped():
    out = md_to_html("a & b < c > d")
    assert out == "a &amp; b &lt; c &gt; d"


def test_md_to_html_never_raises_on_arbitrary_input():
    for bad in ["", "   ", "*" * 500, "`" * 50, "```", None]:
        if bad is None:
            continue
        md_to_html(bad)  # must not raise


def test_secretscan_reports_correct_line_number():
    text = "line one\nline two\n" + "AKIAABCDEFGHIJKLMNOP" + "\nline four"
    r = scan_text(text)
    assert r["count"] == 1
    assert r["findings"][0]["line"] == 3


def test_secretscan_clean_text_finds_nothing():
    r = scan_text("just a normal sentence about domains and emails.")
    assert r["count"] == 0
    assert r["findings"] == []


def test_secretscan_deduplicates_repeated_matches():
    secret = "AKIAABCDEFGHIJKLMNOP"
    r = scan_text(f"{secret}\n...\n{secret}")
    assert r["count"] == 1


# --------------------------------------------------------------------------- #
# TruffleHog wrapper — run_command is mocked (no real subprocess/network in
# the committed suite); the actual binary was verified separately against a
# real downloaded release, including that it correctly ignores a fake
# low-entropy AWS-shaped string the regex scanner above would have flagged.
# --------------------------------------------------------------------------- #
def test_trufflehog_parses_findings_and_masks_secret():
    json_line = (
        '{"SourceMetadata":{"Data":{"Filesystem":{"file":"/tmp/x.txt","line":2}}},'
        '"DetectorName":"Github","Verified":false,'
        '"Raw":"ghp_i0VpEBOWfbZAVaBSo63bbH6xnAbnBEoonCrb"}'
    )
    stdout = (
        '{"level":"info-0","msg":"running source"}\n'
        f"{json_line}\n"
        '{"level":"info-0","msg":"finished scanning"}\n'
    )

    async def fake_run_command(cmd, timeout=120, cwd=None, stdin=None, env=None):
        assert cmd[0] == "trufflehog"
        assert "filesystem" in cmd and "--no-verification" in cmd and "--json" in cmd
        return CommandResult(True, stdout, "", 0)

    async def scenario():
        with patch.object(trufflehog_mod, "run_command", side_effect=fake_run_command):
            return await trufflehog_scan("some text with a token")

    r = asyncio.run(scenario())
    assert r["available"] is True
    assert r["count"] == 1
    f = r["findings"][0]
    assert f["detector"] == "Github"
    assert f["verified"] is False
    assert f["line"] == 2
    assert "ghp_i0VpEBOWfbZAVaBSo63bbH6xnAbnBEoonCrb" not in f["match"]
    assert f["match"].startswith("ghp_i0")


def test_trufflehog_ignores_non_finding_log_lines():
    stdout = '{"level":"info-0","msg":"finished scanning","chunks":1}\n'

    async def fake_run_command(cmd, timeout=120, cwd=None, stdin=None, env=None):
        return CommandResult(True, stdout, "", 0)

    async def scenario():
        with patch.object(trufflehog_mod, "run_command", side_effect=fake_run_command):
            return await trufflehog_scan("clean text, nothing here")

    r = asyncio.run(scenario())
    assert r["available"] is True
    assert r["count"] == 0
    assert r["findings"] == []


def test_trufflehog_reports_not_installed_cleanly():
    async def fake_run_command(cmd, timeout=120, cwd=None, stdin=None, env=None):
        return CommandResult(False, "", "trufflehog not installed", None, missing=True)

    async def scenario():
        with patch.object(trufflehog_mod, "run_command", side_effect=fake_run_command):
            return await trufflehog_scan("text")

    r = asyncio.run(scenario())
    assert r["available"] is False
    assert "reason" in r


def test_trufflehog_cleans_up_its_temp_file():
    seen_paths = []

    async def fake_run_command(cmd, timeout=120, cwd=None, stdin=None, env=None):
        path = cmd[-1]
        seen_paths.append(path)
        assert Path(path).exists()  # the scanned text really was written there
        return CommandResult(True, "", "", 0)

    async def scenario():
        with patch.object(trufflehog_mod, "run_command", side_effect=fake_run_command):
            await trufflehog_scan("text to scan")

    asyncio.run(scenario())
    assert seen_paths and not Path(seen_paths[0]).exists()


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


# --------------------------------------------------------------------------- #
# PluginService — owner-installed runtime tools (pipx). No real network/pipx
# calls here (run_command is mocked); the actual pipx/pip mechanics were
# verified separately against a real PyPI package during development.
# --------------------------------------------------------------------------- #
def test_plugin_install_rejects_bad_id_and_bad_spec():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            c = Container.build(s)
            await c.startup()
            await c.access.register_seen(1, "o", "O")

            bad_id = await c.plugins.install(1, "Not Valid | somepkg")
            bad_spec = await c.plugins.install(1, "goodid | pkg; rm -rf /")
            too_few_parts = await c.plugins.install(1, "onlyid")
            await c.shutdown()
            return bad_id, bad_spec, too_few_parts

    bad_id, bad_spec, too_few_parts = asyncio.run(scenario())
    assert bad_id["available"] is False
    assert bad_spec["available"] is False
    assert too_few_parts["available"] is False


def test_plugin_install_rejects_id_already_taken():
    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            c = Container.build(s)
            await c.startup()
            await c.access.register_seen(1, "o", "O")
            res = await c.plugins.install(1, "whois | some-other-whois-package")
            await c.shutdown()
            return res

    res = asyncio.run(scenario())
    assert res["available"] is False
    assert "занят" in res["reason"]


def test_plugin_install_full_roundtrip_with_mocked_pipx(tmp_path, monkeypatch):
    """Install -> live-registered -> runnable -> listed -> removed -> survives
    a simulated restart (bootstrap reloads from DB)."""
    monkeypatch.setattr(plugins_mod, "PIPX_HOME", str(tmp_path / "pipx"))
    bin_dir = tmp_path / "pipx" / "bin"
    monkeypatch.setattr(plugins_mod, "PIPX_BIN_DIR", str(bin_dir))
    bin_dir.mkdir(parents=True)
    fake_bin = bin_dir / "fakebin"
    fake_bin.write_text("#!/bin/sh\necho fake output\n")
    fake_bin.chmod(0o755)

    list_calls = {"n": 0}

    async def fake_run_command(cmd, timeout=120, cwd=None, stdin=None, env=None):
        if cmd[:2] == ["pipx", "list"]:
            list_calls["n"] += 1
            body = ('{"venvs": {}}' if list_calls["n"] == 1 else
                    json.dumps({"venvs": {"fakepkg": {
                        "metadata": {"main_package": {"apps": ["fakebin"]}}}}}))
            return CommandResult(True, body, "", 0)
        if cmd[:2] == ["pipx", "install"] or cmd[:2] == ["pipx", "uninstall"]:
            return CommandResult(True, "ok", "", 0)
        if cmd and cmd[0] == str(fake_bin):
            return CommandResult(True, "fake output", "", 0)
        return CommandResult(False, "", f"{cmd[0] if cmd else '?'} not installed", None, missing=True)

    async def scenario():
        with tempfile.TemporaryDirectory() as tmp:
            s = load_settings()
            s.database_path = str(Path(tmp) / "t.db")
            c = Container.build(s)
            await c.startup()
            await c.access.register_seen(1, "o", "O")

            with patch.object(plugins_mod, "run_command", side_effect=fake_run_command):
                install_res = await c.plugins.install(
                    1, "fake_tool | fakepkg | FakeTool | a fake tool for tests")
                assert install_res["available"] is True, install_res
                assert "fake_tool" in TOOLS

                tool = TOOLS["fake_tool"]
                run_result = await tool.run(c, 1, "target")
                assert "fake output" in run_result.text

                listing = await c.plugins.list_installed()
                assert listing["count"] == 1

                remove_res = await c.plugins.remove("fake_tool")
                assert remove_res["available"] is True
                assert "fake_tool" not in TOOLS

                install_res2 = await c.plugins.install(
                    1, "fake_tool | fakepkg | FakeTool | a fake tool for tests")
                assert install_res2["available"] is True

            # Simulate a process restart: wipe the in-memory registry, then
            # confirm bootstrap() restores it from the DB alone.
            del TOOLS["fake_tool"]
            assert "fake_tool" not in TOOLS
            await c.plugins.bootstrap()
            assert "fake_tool" in TOOLS

            await c.shutdown()

    asyncio.run(scenario())
