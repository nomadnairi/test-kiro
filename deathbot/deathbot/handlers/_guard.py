"""Shared access-guard helper used at the top of module handlers."""
from __future__ import annotations

from aiogram.types import Message

from ..container import Container

_REASONS = {
    "banned": "🚫 You are banned.",
    "not_whitelisted": "🔒 Access denied. You are not whitelisted. Ask the owner for an invite.",
    "module_disabled": "⛔ This module is currently disabled.",
    "insufficient_role": "⛔ Your role does not permit this action.",
}


async def guard(message: Message, container: Container, module: str) -> bool:
    """Return True if the user may use ``module``; otherwise reply and return False."""
    user = message.from_user
    if user is None:
        return False
    decision = await container.access.check(user.id, module)
    if not decision.allowed:
        await message.answer(_REASONS.get(decision.reason, "⛔ Access denied."))
    return decision.allowed
