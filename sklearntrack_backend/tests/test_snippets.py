import pytest
from notes.models import CodeSnippet

@pytest.mark.django_db
def test_create_snippet(auth_client):
    response = auth_client.post("/api/snippets/", {  # ← Changed URL
        "title": "Python Loop",
        "language": "python",
        "code": "for i in range(5): print(i)"
    })
    assert response.status_code == 201
    assert CodeSnippet.objects.count() == 1