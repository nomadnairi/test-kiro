"""The entire button UI: menu navigation + a registry-driven tool runner.

There are no feature commands — every capability is reached by tapping buttons.
Only /start, /menu and /cancel exist to bootstrap or reset the interface.
"""
from __future__ import annotations

import io
from html import escape as escape_html

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from datetime import datetime, timezone

from ..container import Container
from ..keyboards import cancel_menu, category_menu, export_menu, main_menu, result_menu
from ..registry import Result, Tool, build_export, get_tool, save_last_report, strip_html
from ..states import AIChat, ApiKeyFlow, ToolFlow
from ..util import truncate, validate_input

router = Router(name="menu")

_REASONS = {
    "banned": "🚫 Ты забанен.",
    "not_whitelisted": "🔒 Доступ закрыт — тебя нет в списке. Попроси доступ у владельца.",
    "module_disabled": "⛔ Этот раздел отключён.",
    "insufficient_role": "⛔ Твоя роль не позволяет это.",
}
_WELCOME = (
    "💀 <b>DeathBot</b>\n"
    "Всё управляется кнопками ниже — просто нажимай.\n"
    "OSINT · Пентест · ИИ · Агенты · Заметки · Экспорт"
)


def _visible(container: Container, role: str):
    """Sync predicate for menu building (role matrix + owner)."""
    return lambda module: container.access.role_can_use(role, module)


async def _deny_reason(container: Container, uid: int, module: str) -> str | None:
    decision = await container.access.check(uid, module)
    return None if decision.allowed else _REASONS.get(decision.reason, "⛔ Доступ закрыт.")


# --------------------------------------------------------------------------- #
# entry commands (the only commands that exist)
# --------------------------------------------------------------------------- #
@router.message(CommandStart())
@router.message(Command("menu"))
async def cmd_menu(message: Message, container: Container, state: FSMContext,
                   role: str = "guest") -> None:
    await state.clear()
    await message.answer(_WELCOME, reply_markup=main_menu(_visible(container, role)))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, container: Container, state: FSMContext,
                     role: str = "guest") -> None:
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu(_visible(container, role)))


# --------------------------------------------------------------------------- #
# navigation callbacks
# --------------------------------------------------------------------------- #
@router.callback_query(F.data == "nav:main")
async def cb_main(cb: CallbackQuery, container: Container, state: FSMContext,
                  role: str = "guest") -> None:
    await state.clear()
    await cb.message.edit_text(_WELCOME, reply_markup=main_menu(_visible(container, role)))
    await cb.answer()


@router.callback_query(F.data == "nav:cancel")
async def cb_cancel(cb: CallbackQuery, container: Container, state: FSMContext,
                    role: str = "guest") -> None:
    await state.clear()
    await cb.message.edit_text(_WELCOME, reply_markup=main_menu(_visible(container, role)))
    await cb.answer("Отменено")


@router.callback_query(F.data == "exp:pick")
async def cb_export_pick(cb: CallbackQuery, container: Container) -> None:
    formats = container.export.available_formats()
    await cb.message.answer(
        "📤 <b>Сохранить последний результат</b>\nВыбери формат:",
        reply_markup=export_menu(formats, container.export.LABELS),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("exp:fmt:"))
async def cb_export_fmt(cb: CallbackQuery, container: Container) -> None:
    fmt = cb.data.split(":", 2)[2]
    await cb.answer("Готовлю файл…")
    try:
        result = await build_export(container, cb.from_user.id, fmt)
    except Exception as exc:  # noqa: BLE001
        await cb.message.answer(f"⚠️ Не удалось экспортировать: {exc}")
        return
    await cb.message.answer_document(
        BufferedInputFile(result.file_bytes, filename=result.filename),
        caption=result.text,
    )


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cb: CallbackQuery, container: Container, state: FSMContext,
                      role: str = "guest") -> None:
    await state.clear()
    category = cb.data.split(":", 1)[1]
    from ..registry import CATEGORIES, tools_in
    label = dict(CATEGORIES).get(category, category)
    vis = _visible(container, role)
    # Legend: name — what it does, so the user knows each tool before tapping.
    legend = "\n".join(
        f"• <b>{escape_html(t.label)}</b> — {escape_html(t.desc)}" if t.desc
        else f"• <b>{escape_html(t.label)}</b>"
        for t in tools_in(category) if vis(t.module)
    )
    text = f"{label}\n\n{legend}\n\nВыбери инструмент 👇" if legend else f"{label}\nВыбери инструмент:"
    await cb.message.edit_text(text[:4000], reply_markup=category_menu(category, vis))
    await cb.answer()


# --------------------------------------------------------------------------- #
# tool tap
# --------------------------------------------------------------------------- #
@router.callback_query(F.data.startswith("tool:"))
async def cb_tool(cb: CallbackQuery, container: Container, state: FSMContext) -> None:
    tool = get_tool(cb.data.split(":", 1)[1])
    if tool is None:
        await cb.answer("Неизвестный инструмент", show_alert=True)
        return

    reason = await _deny_reason(container, cb.from_user.id, tool.module)
    if reason:
        await cb.answer(reason, show_alert=True)
        return

    if tool.kind == "instant":
        await cb.answer("Выполняю…")
        await _run_and_reply(cb.message, container, cb.from_user.id, tool, "")
        return

    if tool.kind == "chat":
        await state.set_state(AIChat.chatting)
        await cb.message.edit_text(
            "💬 <b>Режим диалога</b> — пиши сообщения. Нажми «Отмена», чтобы выйти.",
            reply_markup=cancel_menu(),
        )
        await cb.answer()
        return

    if tool.kind == "apikey":
        await state.set_state(ApiKeyFlow.waiting_provider)
        await cb.message.edit_text(
            "Какой провайдер?\n\n"
            "<b>ИИ:</b> openai, openrouter, groq, deepseek, grok, claude, gemini\n"
            "<b>OSINT:</b> shodan, hibp, abuseipdb, dehashed, virustotal, hunter, securitytrails\n\n"
            "Ключ заработает сразу после сохранения, приоритет — над ключом в .env.",
            reply_markup=cancel_menu(),
        )
        await cb.answer()
        return

    # input / photo → stash the tool and prompt
    await state.set_state(ToolFlow.waiting_photo if tool.kind == "photo" else ToolFlow.waiting_input)
    await state.update_data(tool_id=tool.id, category=tool.category)
    parts = [f"<b>{tool.label}</b>"]
    if tool.desc:
        parts.append(f"<i>{tool.desc}</i>")
    parts.append(f"\n{tool.prompt}")
    await cb.message.edit_text("\n".join(parts), reply_markup=cancel_menu())
    await cb.answer()


# --------------------------------------------------------------------------- #
# input dispatch
# --------------------------------------------------------------------------- #
@router.message(ToolFlow.waiting_input, F.text & ~F.text.startswith("/"))
async def on_input(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    tool = get_tool(data.get("tool_id", ""))
    if tool is None or tool.run is None:
        await state.clear()
        await message.answer("Сессия истекла — открой /menu заново.")
        return
    # Validate before running; on failure keep the state so the user can just
    # resend a corrected value.
    if tool.validate:
        err = validate_input(tool.validate, message.text)
        if err:
            await message.answer(err + "\n\nОтправь ещё раз или нажми «Отмена».",
                                 reply_markup=cancel_menu())
            return
    await state.clear()
    await message.chat.do("typing")
    await _run_and_reply(message, container, message.from_user.id, tool, message.text)


@router.message(ToolFlow.waiting_photo, F.photo | F.document)
async def on_photo(message: Message, container: Container, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("category", "osint")
    await state.clear()
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    buf = io.BytesIO()
    await message.bot.download(file_id, destination=buf)
    result = container.osint.exif(buf.getvalue())
    from ..registry import human
    text = human("Метаданные / EXIF", result)
    await save_last_report(container, message.from_user.id, {
        "title": "Metadata / EXIF",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tags": ["deathbot", "osint", "exif"],
        "sections": {"EXIF": strip_html(text)},
    })
    await message.answer(text, reply_markup=result_menu(category, exportable=True))


@router.message(AIChat.chatting, F.text & ~F.text.startswith("/"))
async def on_chat(message: Message, container: Container) -> None:
    await message.chat.do("typing")
    answer = await container.ai.ask(message.from_user.id, message.text)
    await message.answer(truncate(answer), reply_markup=cancel_menu())


# ---- API-key two-step flow ----
@router.message(ApiKeyFlow.waiting_provider, F.text & ~F.text.startswith("/"))
async def on_key_provider(message: Message, state: FSMContext) -> None:
    await state.update_data(provider=message.text.strip().lower())
    await state.set_state(ApiKeyFlow.waiting_value)
    await message.answer("Теперь отправь API-ключ. Он будет зашифрован (AES-256-GCM).",
                         reply_markup=cancel_menu())


@router.message(ApiKeyFlow.waiting_value, F.text & ~F.text.startswith("/"))
async def on_key_value(message: Message, container: Container, state: FSMContext) -> None:
    from ..services.ai import _AI_PROVIDER_IDS
    from ..services.osint import OSINT_KEY_IDS

    data = await state.get_data()
    provider = data.get("provider", "unknown")
    await container.api_keys.set_key(message.from_user.id, provider, message.text.strip())
    await state.clear()
    try:
        await message.delete()  # scrub the plaintext key from the chat
    except Exception:  # noqa: BLE001
        pass

    if provider in _AI_PROVIDER_IDS:
        note = "используется в 🤖 ИИ и 🧠 Агентах."
    elif provider in OSINT_KEY_IDS:
        note = "используется в соответствующем инструменте OSINT."
    else:
        note = ("⚠️ не похоже на известный id — ни один инструмент его не использует. "
               "Проверь список в подсказке выше.")
    await message.answer(f"🔐 Ключ для «{provider}» сохранён (зашифрован) — {note}",
                         reply_markup=result_menu("settings"))


# ---- fallback: any stray text opens the menu ----
@router.message(F.text)
async def on_stray(message: Message, container: Container, role: str = "guest") -> None:
    await message.answer(_WELCOME, reply_markup=main_menu(_visible(container, role)))


# --------------------------------------------------------------------------- #
# shared runner
# --------------------------------------------------------------------------- #
async def _remember(container: Container, uid: int, tool: Tool, arg: str,
                    result: Result) -> None:
    """Store the result so the user can re-export it in any format."""
    report = result.report or {
        "title": f"{tool.label}{f': {arg}' if arg else ''}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tags": ["deathbot", tool.category],
        "sections": {tool.label: strip_html(result.text)},
    }
    await save_last_report(container, uid, report)


async def _deliver(message: Message, placeholder: Message | None, container: Container,
                   uid: int, tool: Tool, arg: str, result: Result) -> None:
    if result.file_bytes is not None and result.filename:
        await message.answer_document(
            BufferedInputFile(result.file_bytes, filename=result.filename),
            caption=result.text or None,
        )
        done = "Готово."
        if placeholder is not None:
            await placeholder.edit_text(done, reply_markup=result_menu(tool.category))
        else:
            await message.answer(done, reply_markup=result_menu(tool.category))
        return

    await _remember(container, uid, tool, arg, result)
    kb = result_menu(tool.category, exportable=True)
    text = truncate(result.text)
    if placeholder is not None:
        await placeholder.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


async def _run_and_reply(message: Message, container: Container, uid: int,
                         tool: Tool, arg: str) -> None:
    # Slow tools run through the task engine so the chat isn't frozen for minutes.
    if tool.background:
        placeholder = await message.answer(
            f"⏳ <b>{tool.label}</b> — выполняется, это может занять пару минут…"
        )

        async def job() -> None:
            try:
                result = await tool.run(container, uid, arg)
            except Exception as exc:  # noqa: BLE001
                await placeholder.edit_text(
                    f"⚠️ Ошибка «{tool.label}»: {exc}",
                    reply_markup=result_menu(tool.category),
                )
                return
            await _deliver(message, placeholder, container, uid, tool, arg, result)

        container.engine.submit(job, timeout=420, retries=1)
        return

    try:
        result = await tool.run(container, uid, arg)
    except Exception as exc:  # noqa: BLE001 — surface tool errors to the user
        await message.answer(f"⚠️ Ошибка «{tool.label}»: {exc}",
                             reply_markup=result_menu(tool.category))
        return
    await _deliver(message, None, container, uid, tool, arg, result)
