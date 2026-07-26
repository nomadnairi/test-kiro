"""NotificationService — push messages to users/owner out of band."""
from __future__ import annotations

from ..logging_setup import get_logger

log = get_logger("svc.notify")


class NotificationService:
    def __init__(self, bot, owner_id: int) -> None:
        self._bot = bot
        self._owner_id = owner_id

    async def send(self, chat_id: int, text: str) -> None:
        try:
            await self._bot.send_message(chat_id, text)
        except Exception as exc:  # noqa: BLE001 — bot may be offline in tests
            log.warning("notify %s failed: %s", chat_id, exc)

    async def notify_owner(self, text: str) -> None:
        if self._owner_id:
            await self.send(self._owner_id, text)
