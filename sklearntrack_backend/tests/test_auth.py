import uuid
import pytest

@pytest.mark.django_db
def test_register(api_client):
    response = api_client.post("/api/auth/register/", {
        "email": f"user_{uuid.uuid4()}@example.com",
        "username": "newuser",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "full_name": "New User",
        "country": "PK",
        "education_level": "undergraduate",
        "field_of_study": "CS",
        "terms_accepted": True
    })
    assert response.status_code == 201


@pytest.mark.django_db
def test_login(api_client, user):
    response = api_client.post("/api/token/", {
        "email": user.email,
        "password": "SecurePass123!"
    })
    assert "access" in response.data
