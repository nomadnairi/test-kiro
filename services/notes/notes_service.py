from database.repositories.notes import NoteRepository, Note
from typing import List

class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def add_note(self, user_id: int, title: str, content: str, category: str = "", priority: int = 0, is_pinned: bool = False) -> Note:
        return self.repository.create(user_id, title, content, category, priority, is_pinned)

    def get_user_notes(self, user_id: int) -> List[Note]:
        return self.repository.get_by_user(user_id)

    def update_note(self, user_id: int, note_id: int, title: str, content: str, category: str, priority: int, is_pinned: bool) -> bool:
        return self.repository.update(user_id, note_id, title, content, category, priority, is_pinned)

    def delete_note(self, user_id: int, note_id: int) -> bool:
        return self.repository.delete(user_id, note_id)
