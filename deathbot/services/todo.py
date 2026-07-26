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
