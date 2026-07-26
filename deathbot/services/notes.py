"""NotesService."""
from __future__ import annotations

from ..repositories import Repositories


class NotesService:
    def __init__(self, repos: Repositories) -> None:
        self.repos = repos

    async def add(self, user_id: int, text: str) -> int:
        title, _, body = text.partition("\n")
        note_id = await self.repos.notes.add(user_id, title.strip()[:120], body.strip())
        await self.repos.audit.log(user_id, "note.add", str(note_id))
        return note_id

    async def list(self, user_id: int) -> list[dict]:
        return [dict(r) for r in await self.repos.notes.list(user_id)]

    async def delete(self, user_id: int, note_id: int) -> bool:
        ok = await self.repos.notes.delete(note_id, user_id)
        if ok:
            await self.repos.audit.log(user_id, "note.delete", str(note_id))
        return ok
