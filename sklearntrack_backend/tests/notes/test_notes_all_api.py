from django.urls import reverse
import pytest
from notes.models import Note, NoteVersion

# ------------------------------------------------------------------
# NOTES CRUD
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_notes_crud_flow(auth_client, user):
    # CREATE
    create_res = auth_client.post(
        "/api/notes/",
        {
            "title": "Test Note",
            "content": "Initial content",
            "status": "draft"
        },
        format="json"
    )
    assert create_res.status_code == 201
    note_id = create_res.data["id"]

    # LIST
    list_res = auth_client.get("/api/notes/")
    assert list_res.status_code == 200
    assert len(list_res.data) >= 1

    # DETAIL
    detail_res = auth_client.get(f"/api/notes/{note_id}/")
    assert detail_res.status_code == 200
    assert detail_res.data["title"] == "Test Note"

    # UPDATE
    update_res = auth_client.put(
        f"/api/notes/{note_id}/",
        {
            "title": "Updated Note",
            "content": "Updated content",
            "status": "published"
        },
        format="json"
    )
    assert update_res.status_code == 200

    # VERSION CREATED
    assert NoteVersion.objects.filter(note_id=note_id).exists()

    # DELETE
    delete_res = auth_client.delete(f"/api/notes/{note_id}/")
    assert delete_res.status_code == 204


# ------------------------------------------------------------------
# VERSION HISTORY + RESTORE
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# DUPLICATE NOTE
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_duplicate_note(auth_client, user):
    note = Note.objects.create(
        user=user,
        title="Original",
        content="Duplicate me"
    )

    res = auth_client.post(f"/api/notes/{note.id}/duplicate/")
    assert res.status_code == 201
    assert Note.objects.count() == 2


# ------------------------------------------------------------------
# AI ACTIONS
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# YOUTUBE IMPORT
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# DAILY NOTES
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_daily_notes(auth_client):
    res = auth_client.get("/api/notes/daily_notes/")
    assert res.status_code == 200


# ------------------------------------------------------------------
# PDF EXPORT
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_note_versions_and_restore(auth_client, user):
    # Create a note via API
    create_res = auth_client.post(
        reverse('note-list'),  # Assuming router names 'note-list'
        {"title": "Versioned", "content": "V1"},
        format="json"
    )
    assert create_res.status_code == 201
    note_id = create_res.data["id"]

    # Update the note (to create a new version)
    update_res = auth_client.put(
        reverse('note-detail', args=[note_id]),
        {"title": "Versioned", "content": "V2"},
        format="json"
    )
    assert update_res.status_code == 200

    # Get versions of the note
    versions_res = auth_client.get(reverse('note-versions', args=[note_id]))
    assert versions_res.status_code == 200
    assert len(versions_res.data) >= 1


@pytest.mark.django_db
def test_ai_action_summarize(auth_client, user):
    # Create a note directly
    note = Note.objects.create(
        user=user,
        title="AI Note",
        content="This is a long content for AI summarization"
    )

    # Call AI action endpoint with correct keys and valid action_type
    res = auth_client.post(
        "/api/notes/ai_action/",
        {
            "action_type": "summarize_short",
            "content": note.content,
            "note_id": note.id
        },
        format="json"
    )

    # Adjust this assert based on your view's expected response code for success
    assert res.status_code in [200, 202]


@pytest.mark.django_db
def test_import_youtube(auth_client, user):
    # Create a note to associate (if needed)
    note = Note.objects.create(
        user=user,
        title="YT",
        content=""
    )

    # Post to import_youtube with correct keys per serializer
    res = auth_client.post(
        "/api/notes/import_youtube/",
        {
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "generate_notes": True,
            "note_title": "Test YT Notes"
        },
        format="json"
    )

    assert res.status_code in [200, 201, 202]


@pytest.mark.django_db
def test_export_pdf(auth_client, user):
    # Create a published note for export
    note = Note.objects.create(
        user=user,
        title="PDF Test",
        content="Export this note",
        status="published"
    )

    # Export PDF via API
    res = auth_client.post(f"/api/notes/{note.id}/export_pdf/")

    assert res.status_code == 200

# ------------------------------------------------------------------
# AUTH CHECK
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_notes_unauthorized_access(api_client):
    res = api_client.get("/api/notes/")
    assert res.status_code == 401
