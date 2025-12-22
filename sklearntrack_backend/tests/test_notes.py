import pytest
from notes.models import Note

@pytest.mark.django_db
def test_create_note(auth_client):
    response = auth_client.post("/api/notes/", {
        "title": "Pytest Note",
        "content": "Learning pytest deeply"
    })
    assert response.status_code == 201
    assert Note.objects.count() == 1


@pytest.mark.django_db
def test_note_history_created(auth_client, user):
    note = Note.objects.create(
        user=user,
        title="History",
        content="v1"
    )
    response = auth_client.patch(f"/api/notes/{note.id}/", {
        "title": "History",
        "content": "v2"
    })
    assert response.status_code == 200
