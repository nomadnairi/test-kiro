"""UserService — profile + user administration."""
from __future__ import annotations

from ..repositories import Repositories


class UserService:
    def __init__(self, repos: Repositories) -> None:
        self.repos = repos

    async def profile(self, user_id: int) -> dict:
        user = await self.repos.users.get(user_id)
        if user is None:
            return {}
        notes = await self.repos.notes.list(user_id, limit=1000)
        todos = await self.repos.todos.list(user_id)
        providers = await self.repos.api_keys.list_providers(user_id)
        return {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "created_at": user["created_at"],
            "notes": len(notes),
            "todos": len(todos),
            "providers": providers,
        }

    async def list_users(self, limit: int = 50) -> list[dict]:
        rows = await self.repos.users.list_all(limit)
        return [dict(r) for r in rows]

    async def stats(self) -> dict:
        return {"users": await self.repos.users.count()}
