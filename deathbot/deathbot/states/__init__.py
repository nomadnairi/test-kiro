"""FSM state groups."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AIChat(StatesGroup):
    chatting = State()


class NoteFlow(StatesGroup):
    waiting_text = State()


class TodoFlow(StatesGroup):
    waiting_text = State()


class ApiKeyFlow(StatesGroup):
    waiting_provider = State()
    waiting_value = State()
