"""Todo CRUD."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from ..container import Container
from ._guard import guard

router = Router(name="todo")


@router.message(Command("todo"))
async def cmd_todo_add(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "todo"):
        return
    if not command.args:
        await message.answer("Usage: <code>/todo buy milk</code>")
        return
    todo_id = await container.todos.add(message.from_user.id, command.args)
    await message.answer(f"✅ Added todo #{todo_id}")


@router.message(Command("todos"))
async def cmd_todos_list(message: Message, container: Container) -> None:
    if not await guard(message, container, "todo"):
        return
    todos = await container.todos.list(message.from_user.id)
    if not todos:
        await message.answer("No todos. Add one with <code>/todo text</code>.")
        return
    lines = [f"{'☑️' if t['done'] else '⬜'} #{t['id']} {t['text']}" for t in todos]
    await message.answer("<b>Your todos</b>\n" + "\n".join(lines))


@router.message(Command("done"))
async def cmd_todo_done(message: Message, command: CommandObject, container: Container) -> None:
    if not await guard(message, container, "todo"):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: <code>/done &lt;id&gt;</code>")
        return
    ok = await container.todos.done(message.from_user.id, int(command.args.strip()))
    await message.answer("☑️ Completed." if ok else "Not found.")
