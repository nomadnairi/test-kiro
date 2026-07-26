"""Base repository — holds the shared Database handle."""
from __future__ import annotations

from ..db import Database


class BaseRepository:
    def __init__(self, db: Database) -> None:
        self.db = db
