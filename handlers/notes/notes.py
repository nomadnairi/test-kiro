# Dummy handler to represent routing.
from services.notes.notes_service import NoteService
from database.repositories.notes import NoteRepository

repository = NoteRepository()
service = NoteService(repository)

def handle_add_note(user_id: int, title: str, content: str):
    return service.add_note(user_id, title, content)
