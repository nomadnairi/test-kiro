"""Role definitions and ordering used by the permission matrix."""
from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"
    GUEST = "guest"


# Higher index == more privileged. Used for "at least this role" checks.
ROLE_ORDER: list[str] = [
    Role.GUEST.value,
    Role.USER.value,
    Role.ANALYST.value,
    Role.ADMIN.value,
    Role.OWNER.value,
]


def role_rank(role: str) -> int:
    try:
        return ROLE_ORDER.index(role)
    except ValueError:
        return 0


def at_least(role: str, minimum: str) -> bool:
    return role_rank(role) >= role_rank(minimum)
