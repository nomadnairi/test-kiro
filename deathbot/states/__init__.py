"""FSM state groups."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AIChat(StatesGroup):
    chatting = State()


class ToolFlow(StatesGroup):
    waiting_input = State()   # generic tool text input (data: tool_id, category)
    waiting_photo = State()   # EXIF: waiting for an image


class ApiKeyFlow(StatesGroup):
    waiting_provider = State()
    waiting_value = State()
