"""Offline smoke test — exercises every layer without touching Telegram.

Run:  python smoke_test.py
Covers: schema init, container wiring, crypto, access control, notes/todo,
encrypted keys, the AI router fallback, all export formats, the tool registry
integrity, keyboard generation, dispatcher build, and a set of offline tool runs.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from deathbot.ai import ChatMessage, ProviderError
from deathbot.bot import build_dispatcher
from deathbot.config import load_settings
from deathbot.container import Container
from deathbot.keyboards import category_menu, main_menu
from deathbot.registry import CATEGORIES, TOOLS, get_tool, tools_in


async def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok))
        print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as tmp:
        settings = load_settings()
        settings.database_path = str(Path(tmp) / "smoke.sqlite3")
        settings.owner_id = 42
        settings.raw.setdefault("bot", {})["whitelist_only"] = True

        container = Container.build(settings)
        await container.startup()
        check("container + schema", Path(settings.database_path).exists())

        # crypto
        tok = container.crypto.encrypt("secret", aad=b"42:x")
        check("AES-256-GCM round-trip", container.crypto.decrypt(tok, aad=b"42:x") == "secret")

        # access / whitelist / rbac
        check("owner auto-promote", await container.access.register_seen(42, "o", "O") == "owner")
        await container.access.register_seen(99, "g", "G")
        check("guest blocked", not (await container.access.check(99, "osint")).allowed)
        await container.access.grant(42, 99, "analyst")
        check("granted analyst passes", (await container.access.check(99, "osint")).allowed)

        # productivity
        nid = await container.notes.add(42, "T\nbody")
        check("notes CRUD", bool(nid) and len(await container.notes.list(42)) == 1)
        tid = await container.todos.add(42, "x")
        check("todo done", await container.todos.done(42, tid))

        # encrypted keys
        await container.api_keys.set_key(42, "openai", "sk-1")
        check("encrypted key", await container.api_keys.get_key(42, "openai") == "sk-1")

        # AI providers registered (all 10)
        check("AI providers registered (10)",
              len(container.ai_router._providers) == 10,
              ", ".join(sorted(container.ai_router._providers)))

        # AI router degrades gracefully with no keys
        try:
            await container.ai_router.chat([ChatMessage("user", "hi")])
            routed_ok = False
        except ProviderError:
            routed_ok = True
        check("AI router graceful w/o keys", routed_ok)

        # agents (all 8)
        check("agents registered (8)", len(container.agents) == 8, ", ".join(sorted(container.agents)))

        # export — all 6 formats produce bytes
        rep = container.report.build("t", {"a": {"x": 1}})
        fmts = {f: len(container.export.render(rep, f)) for f in
                ("json", "markdown", "html", "csv", "pdf", "docx")}
        check("export all 6 formats", all(v > 0 for v in fmts.values()), str(fmts))

        # registry integrity
        need_run = [t.id for t in TOOLS.values() if t.kind in ("input", "instant") and t.run is None]
        check("registry: every runnable tool has run()", not need_run, str(need_run))
        check("registry: 8 categories populated", all(tools_in(c) for c, _ in CATEGORIES),
              f"{len(TOOLS)} tools")

        # keyboards
        vis = lambda m: container.access.role_can_use("owner", m)  # noqa: E731
        km = main_menu(vis)
        check("main menu built", len(km.inline_keyboard) > 0)
        check("every category menu builds", all(
            category_menu(c, vis).inline_keyboard for c, _ in CATEGORIES))

        # offline tool runs (no network / no external binary)
        ioc = await get_tool("ioc").run(container, 42, "8.8.8.8")
        check("tool run: IOC classify", "ipv4" in ioc.text)
        exp = await get_tool("exp_json").run(container, 42, "")
        check("tool run: export file", exp.file_bytes is not None and exp.filename.endswith(".json"))
        prof = await get_tool("profile").run(container, 42, "")
        check("tool run: profile", "роль" in prof.text.lower())

        # dispatcher
        dp = build_dispatcher(container)
        msg_h = len(dp.message.handlers) + sum(len(r.message.handlers) for r in _walk(dp))
        cb_h = len(dp.callback_query.handlers) + sum(len(r.callback_query.handlers) for r in _walk(dp))
        check("dispatcher: message + callback handlers", msg_h > 0 and cb_h > 0,
              f"{msg_h} msg / {cb_h} callback")

        await container.shutdown()

    passed = sum(1 for _, ok in checks if ok)
    print("\n" + "=" * 60)
    print(f"{passed}/{len(checks)} checks passed")
    if passed != len(checks):
        raise SystemExit(1)
    print("ALL GREEN ✅")


def _walk(router):
    for sub in router.sub_routers:
        yield sub
        yield from _walk(sub)


if __name__ == "__main__":
    asyncio.run(main())
