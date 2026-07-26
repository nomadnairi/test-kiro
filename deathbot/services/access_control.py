"""AccessControlService — the security heart of the bot.

Combines: owner override, whitelist gate, role-based permission matrix and
audit logging. Every handler goes through :meth:`ensure` (via middleware or a
filter) before doing work.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from ..core.roles import Role, at_least
from ..logging_setup import get_logger
from ..repositories import Repositories

log = get_logger("svc.access")


@dataclass(slots=True)
class AccessDecision:
    allowed: bool
    role: str
    reason: str = ""


class AccessControlService:
    def __init__(self, settings: Settings, repos: Repositories) -> None:
        self.settings = settings
        self.repos = repos

    def is_owner(self, user_id: int) -> bool:
        return self.settings.owner_id != 0 and user_id == self.settings.owner_id

    async def register_seen(self, user_id: int, username: str | None, full_name: str | None) -> str:
        """Upsert the user, auto-promoting the configured owner. Returns role."""
        existing = await self.repos.users.get(user_id)
        if existing is None:
            is_owner = self.is_owner(user_id)
            role = Role.OWNER.value if is_owner else Role.GUEST.value
            # New non-owners land in a pending (inactive) state until an admin
            # activates them — this is what makes `whitelist_only` a real gate.
            await self.repos.users.upsert(
                user_id, username, full_name, role, is_active=1 if is_owner else 0
            )
            await self.repos.audit.log(user_id, "user.first_seen", role)
            return role

        await self.repos.users.upsert(user_id, username, full_name)
        if self.is_owner(user_id) and existing["role"] != Role.OWNER.value:
            await self.repos.users.set_role(user_id, Role.OWNER.value)
            return Role.OWNER.value
        return existing["role"]

    async def get_role(self, user_id: int) -> str:
        if self.is_owner(user_id):
            return Role.OWNER.value
        return (await self.repos.access.get_role(user_id)) or Role.GUEST.value

    def role_can_use(self, role: str, module: str) -> bool:
        if role == Role.OWNER.value:
            return True
        allowed = self.settings.role_matrix.get(role, [])
        return "*" in allowed or module in allowed

    async def check(self, user_id: int, module: str) -> AccessDecision:
        role = await self.get_role(user_id)

        if self.is_owner(user_id):
            return AccessDecision(True, role)

        user = await self.repos.users.get(user_id)
        if user is not None and user["is_banned"]:
            return AccessDecision(False, role, "banned")

        if self.settings.whitelist_only and not await self.repos.access.is_whitelisted(user_id):
            return AccessDecision(False, role, "not_whitelisted")

        if not self.settings.module_enabled(module) and module not in ("profile",):
            return AccessDecision(False, role, "module_disabled")

        if not self.role_can_use(role, module):
            return AccessDecision(False, role, "insufficient_role")

        return AccessDecision(True, role)

    async def require_role(self, user_id: int, minimum: str) -> bool:
        return self.is_owner(user_id) or at_least(await self.get_role(user_id), minimum)

    # ---- admin operations -------------------------------------------------
    async def grant(self, actor_id: int, target_id: int, role: str) -> None:
        await self.repos.users.upsert(target_id, None, None, role)
        await self.repos.users.set_role(target_id, role)
        # Granting a role also whitelists (activates) the user.
        await self.repos.users.set_active(target_id, True)
        await self.repos.audit.log(actor_id, "access.grant", f"{target_id}->{role}")

    async def ban(self, actor_id: int, target_id: int, banned: bool = True) -> None:
        await self.repos.users.set_banned(target_id, banned)
        await self.repos.audit.log(actor_id, "access.ban", f"{target_id}={banned}")
