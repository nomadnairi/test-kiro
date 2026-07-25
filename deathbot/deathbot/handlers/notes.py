"""Notes CRUD (handler → NotesService → NoteRepository → SQLite)."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from ..container import Container
from ._guard import guard

router = Router(name="notes")


@router.message(Command("note"))
async def cmd_note_add(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "notes"):
        return
    if not command.args:
        await message.answer("Usage: <code>/note your text</code>")
        return
    note_id = await container.notes.add(message.from_user.id, command.args)
    await message.answer(f"📝 Saved note #{note_id}")


@router.message(Command("notes"))
async def cmd_notes_list(message: Message, container: Container) -> None:
    if not await guard(message, container, "notes"):
        return
    notes = await container.notes.list(message.from_user.id)
    if not notes:
        await message.answer("No notes yet. Add one with <code>/note text</code>.")
        return
    lines = [f"#{n['id']} <b>{n['title'] or 'untitled'}</b>" for n in notes]
    await message.answer("<b>Your notes</b>\n" + "\n".join(lines))


@router.message(Command("delnote"))
async def cmd_note_del(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "notes"):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: <code>/delnote &lt;id&gt;</code>")
        return
    ok = await container.notes.delete(message.from_user.id, int(command.args.strip()))
    await message.answer("🗑 Deleted." if ok else "Not found.")
