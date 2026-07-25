"""Offline smoke test — exercises every layer without touching Telegram.

Run:  python smoke_test.py
Verifies imports, schema init, the container wiring, the dispatcher/router
registration, and a handful of end-to-end handler→service→repository flows.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from deathbot.ai import ChatMessage, ProviderError
from deathbot.bot import build_dispatcher
from deathbot.config import load_settings
from deathbot.container import Container
from deathbot.core.security import Crypto


def _make_settings(db_path: Path):
    settings = load_settings()
    settings.database_path = str(db_path)
    settings.owner_id = 42
    # Ensure whitelist gating is exercised deterministically.
    settings.raw.setdefault("bot", {})["whitelist_only"] = True
    return settings


async def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))
        print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "smoke.sqlite3"
        settings = _make_settings(db_path)

        # --- container + schema ---
        container = Container.build(settings)
        await container.startup()
        check("container.build + schema init", db_path.exists())

        # --- crypto round-trip ---
        secret = "sk-super-secret-value"
        token = container.crypto.encrypt(secret, aad=b"42:openai")
        back = container.crypto.decrypt(token, aad=b"42:openai")
        check("AES-256-GCM round-trip", back == secret)
        check("Crypto.from_settings 32-byte", isinstance(container.crypto, Crypto))

        # --- owner auto-promotion + access ---
        role = await container.access.register_seen(42, "owner", "The Owner")
        check("owner auto-promote", role == "owner", role)
        owner_dec = await container.access.check(42, "admin")
        check("owner passes admin gate", owner_dec.allowed)

        # --- non-whitelisted guest is blocked ---
        await container.access.register_seen(99, "rando", "Rando")
        guest_dec = await container.access.check(99, "osint")
        check("guest blocked (not whitelisted)", not guest_dec.allowed, guest_dec.reason)

        # --- grant + re-check ---
        await container.access.grant(42, 99, "analyst")
        analyst_dec = await container.access.check(99, "osint")
        check("granted analyst passes osint gate", analyst_dec.allowed, analyst_dec.reason)

        # --- notes CRUD ---
        nid = await container.notes.add(42, "Title\nbody line")
        notes = await container.notes.list(42)
        deleted = await container.notes.delete(42, nid)
        check("notes add/list/delete", bool(nid) and len(notes) == 1 and deleted)

        # --- todo CRUD ---
        tid = await container.todos.add(42, "write tests")
        done = await container.todos.done(42, tid)
        todos = await container.todos.list(42)
        check("todo add/done/list", bool(tid) and done and todos[0]["done"] == 1)

        # --- api key encrypted storage ---
        await container.api_keys.set_key(42, "openai", "sk-abc123")
        got = await container.api_keys.get_key(42, "openai")
        providers = await container.api_keys.list_providers(42)
        check("encrypted api key store/fetch", got == "sk-abc123" and "openai" in providers)

        # --- cache TTL ---
        await container.repos.cache.set("k", "v", ttl_seconds=60)
        cached = await container.repos.cache.get("k")
        check("cache set/get", cached == "v")

        # --- AI router: no keys => graceful ProviderError, service wraps it ---
        providers_avail = container.ai.available_providers()
        try:
            await container.ai_router.chat([ChatMessage("user", "hi")])
            routed_ok = False
        except ProviderError:
            routed_ok = True
        answer = await container.ai.ask(42, "hello")
        check("AI router degrades gracefully (no keys)",
              routed_ok and answer.startswith("⚠️"),
              f"providers={providers_avail}")

        # --- export renderers ---
        report = container.report.build("Test", {"dns": {"a": ["1.2.3.4"]}, "note": "hi"})
        md = container.export.render(report, "markdown")
        js = container.export.render(report, "json")
        formats = container.export.available_formats()
        check("export md/json + format list", md.startswith(b"# Test") and b"Test" in js and "json" in formats)

        # --- dispatcher / router registration ---
        dp = build_dispatcher(container)
        # Count registered message handlers across the router tree.
        handler_count = sum(
            len(r.message.handlers) for r in [dp, *dp.sub_routers, *_walk(dp)]
        )
        check("dispatcher builds + handlers registered", handler_count > 0, f"{handler_count} handlers")

        await container.shutdown()

    failed = [c for c in checks if not c[1]]
    print("\n" + "=" * 60)
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    if failed:
        raise SystemExit(1)
    print("ALL GREEN ✅")


def _walk(router):
    for sub in router.sub_routers:
        yield sub
        yield from _walk(sub)


if __name__ == "__main__":
    asyncio.run(main())
