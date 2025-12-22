import pytest

@pytest.mark.django_db
def test_dashboard(auth_client):
    response = auth_client.get("/api/analytics/dashboard/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_notifications(auth_client):
    response = auth_client.get("/api/analytics/notifications/")
    assert response.status_code == 200
