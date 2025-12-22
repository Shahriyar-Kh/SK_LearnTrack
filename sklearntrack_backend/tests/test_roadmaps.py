import pytest
from roadmaps.models import Roadmap

@pytest.mark.django_db
def test_create_roadmap(auth_client):
    response = auth_client.post("/api/roadmaps/", {
        "title": "Backend Roadmap",
        "description": "Django + DRF"
    })
    assert response.status_code == 201
    assert Roadmap.objects.count() == 1
