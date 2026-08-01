"""TodoService."""
from __future__ import annotations

from ..repositories import Repositories


class TodoService:
    def __init__(self, repos: Repositories) -> None:
        self.repos = repos

    async def add(self, user_id: int, text: str) -> int:
        todo_id = await self.repos.todos.add(user_id, text.strip())
        await self.repos.audit.log(user_id, "todo.add", str(todo_id))
        return todo_id

    async def list(self, user_id: int, include_done: bool = True) -> list[dict]:
        return [dict(r) for r in await self.repos.todos.list(user_id, include_done)]

    async def done(self, user_id: int, todo_id: int) -> bool:
        ok = await self.repos.todos.set_done(todo_id, user_id, True)
        if ok:
            await self.repos.audit.log(user_id, "todo.done", str(todo_id))
        return ok

    async def delete(self, user_id: int, todo_id: int) -> bool:
        return await self.repos.todos.delete(todo_id, user_id)

    async def undo(self, user_id: int, todo_id: int) -> bool:
        ok = await self.repos.todos.set_done(todo_id, user_id, False)
        if ok:
            await self.repos.audit.log(user_id, "todo.undo", str(todo_id))
        return ok

    async def edit(self, user_id: int, todo_id: int, text: str) -> bool:
        ok = await self.repos.todos.update_text(todo_id, user_id, text.strip())
        if ok:
            await self.repos.audit.log(user_id, "todo.edit", str(todo_id))
        return ok

    async def clear_done(self, user_id: int) -> int:
        n = await self.repos.todos.clear_done(user_id)
        await self.repos.audit.log(user_id, "todo.clear_done", str(n))
        return n

    async def counts(self, user_id: int) -> tuple[int, int]:
        return await self.repos.todos.counts(user_id)

    async def delete_all(self, user_id: int) -> int:
        return await self.repos.todos.delete_all(user_id)
