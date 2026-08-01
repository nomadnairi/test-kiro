"""Repository layer — the only place that talks SQL."""
from __future__ import annotations

from dataclasses import dataclass

from ..db import Database
from .access import AccessRepository
from .apikey import ApiKeyRepository
from .audit import AuditRepository
from .cache import CacheRepository
from .customtools import CustomToolRepository
from .history import HistoryRepository
from .invite import InviteRepository
from .note import NoteRepository
from .settings import SettingsRepository
from .todo import TodoRepository
from .user import UserRepository


@dataclass(slots=True)
class Repositories:
    """Bundle of every repository, all sharing one Database handle."""

    users: UserRepository
    access: AccessRepository
    invites: InviteRepository
    audit: AuditRepository
    api_keys: ApiKeyRepository
    notes: NoteRepository
    todos: TodoRepository
    settings: SettingsRepository
    history: HistoryRepository
    cache: CacheRepository
    custom_tools: CustomToolRepository

    @classmethod
    def build(cls, db: Database) -> "Repositories":
        return cls(
            users=UserRepository(db),
            access=AccessRepository(db),
            invites=InviteRepository(db),
            audit=AuditRepository(db),
            api_keys=ApiKeyRepository(db),
            notes=NoteRepository(db),
            todos=TodoRepository(db),
            settings=SettingsRepository(db),
            history=HistoryRepository(db),
            cache=CacheRepository(db),
            custom_tools=CustomToolRepository(db),
        )


__all__ = ["Repositories"]
