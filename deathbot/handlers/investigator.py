"""AI Investigator Telegram flow (PHASE 9): /investigate command + FSM.

User sends a goal ("Проверь example.com максимально подробно"), the bot
classifies the target, plans from the playbook, runs real tools through the
OSINT service with live progress edits, then renders an intelligence-report
card with an AI analysis section.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from ..container import Container
from ..states import InvestigateFlow
from ..tools.investigation import current, open_investigation
from ..tools.investigator import AIInvestigator

router = Router(name="investigator")


def _depth(text: str) -> str:
    lowered = text.lower()
    if any(w in lowered for w in ("максимально", "полностью", "подробно",
                                  "всё", "все", "deep")):
        return "max"
    return "standard"


@router.message(Command("investigate"))
@router.callback_query(F.data == "inv:new")
async def inv_start(message_or_cb: Message | CallbackQuery,
                    container: Container, state: FSMContext) -> None:
    text = ("🔎 <b>AI INVESTIGATOR</b>\n\n"
            "Пришли цель одним сообщением: домен, IP, email, юзернейм или "
            "телефон — и что нужно выяснить.\n\n"
            "<i>Пример: «проверь example.com максимально подробно»</i>")
    if isinstance(message_or_cb, CallbackQuery):
        await message_or_cb.answer()
        if message_or_cb.message is not None:
            await message_or_cb.message.edit_text(text, reply_markup=None)
    else:
        await message_or_cb.answer(text)
    await state.set_state(InvestigateFlow.waiting_goal)


@router.message(InvestigateFlow.waiting_goal, F.text & ~F.text.startswith("/"))
async def inv_run(message: Message, container: Container,
                  state: FSMContext) -> None:
    goal = (message.text or "").strip()
    if not goal:
        return
    await state.clear()

    if message.from_user is None:
        return
    investigator = AIInvestigator(container.ai_router, container.osint)
    inv = open_investigation(message.chat.id, message.from_user.id, goal)

    placeholder = await message.answer(
        f"🧠 <b>Investigation started</b>\n🎯 {goal}\n\n"
        f"{inv.progress_line()}\n⏳ планирование…")

    async def progress(line: str) -> None:
        try:
            await placeholder.edit_text(
                f"🧠 <b>Investigation running</b>\n🎯 {goal}\n\n"
                f"{line}\n{inv.progress_line()}")
        except Exception:  # noqa: BLE001, S110 - edit race is non-fatal
            pass

    # Inline run with live progress edits; TaskEngine bounds each single tool.
    await investigator.investigate(inv, depth=_depth(goal),
                                   progress_cb=progress)

    for chunk in _split(inv.report_card()):
        await message.answer(chunk)
    await state.set_state(None)


def _split(text: str, limit: int = 3800) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    buf = ""
    for line in text.splitlines():
        if len(buf) + len(line) > limit:
            parts.append(buf)
            buf = ""
        buf += line + "\n"
    if buf.strip():
        parts.append(buf)
    return parts


@router.callback_query(F.data == "inv:active")
async def inv_active(cb: CallbackQuery, container: Container) -> None:
    if cb.message is None or isinstance(cb.message, InaccessibleMessage):
        return
    inv = current(cb.message.chat.id)
    if inv is None:
        await cb.answer("Нет активных расследований", show_alert=True)
        return
    await cb.answer()
    await cb.message.edit_text(
        f"▶️ <b>ACTIVE</b>\n{inv.report_card()}"[:4000])
