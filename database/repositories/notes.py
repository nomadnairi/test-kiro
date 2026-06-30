import sqlite3
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Note:
    id: int
    user_id: int
    title: str
    content: str
    category: str
    priority: int
    is_pinned: bool

class NoteRepository:
    def __init__(self, db_path: str = "deathbot.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NOLL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    priority INTEGER DEFAULT 0,
                    is_pinned BOOLEAN DEFAULT FALSE
                )
            """)

    def create(self, user_id: int, title: str, content: str, category: str = "", priority: int = 0, is_pinned: bool = False) -> Note:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO notes (user_id, title, content, category, priority, is_pinned) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, title, content, category, priority, is_pinned)
            )
            note_id = cursor.lastrowid
            return Note(note_id, user_id, title, content, category, priority, is_pinned)

    def get_by_user(self, user_id: int) -> List[Note]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,))
            return [Note(*row) for row in cursor.fetchall()]

    def update(self, user_id: int, note_id: int, title: str, content: str, category: str, priority: int, is_pinned: bool) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE notes SET title = ?, content = ?, category = ?, priority = ?, is_pinned = ? WHERE id = ? AND user_id = ?",
                (title, content, category, priority, is_pinned, note_id, user_id)
            )
            return cursor.rowcount > 0

    def delete(self, user_id: int, note_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
            return cursor.rowcount > 0
