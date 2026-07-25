"""Inline-keyboard builders. All navigation is buttons — no commands."""
from __future__ import annotations

from collections.abc import Callable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .registry import CATEGORIES, tools_in

Visible = Callable[[str], bool]  # module scope -> allowed?


def main_menu(visible: Visible) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat_id, label in CATEGORIES:
        if any(visible(t.module) for t in tools_in(cat_id)):
            kb.button(text=label, callback_data=f"cat:{cat_id}")
    kb.adjust(2)
    return kb.as_markup()


def category_menu(category: str, visible: Visible) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for tool in tools_in(category):
        if visible(tool.module):
            kb.button(text=tool.label, callback_data=f"tool:{tool.id}")
    kb.adjust(3)
    kb.row(InlineKeyboardButton(text="⬅️ Menu", callback_data="nav:main"))
    return kb.as_markup()


def cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✖️ Cancel", callback_data="nav:cancel")]
    ])


def result_menu(category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Back", callback_data=f"cat:{category}"),
        InlineKeyboardButton(text="🏠 Menu", callback_data="nav:main"),
    ]])
