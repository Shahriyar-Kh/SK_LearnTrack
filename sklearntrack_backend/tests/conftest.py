import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Unauthenticated API client"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='SecurePass123!',
        full_name='Test User',
        country='PK',
        education_level='undergraduate',
        field_of_study='CS',
        terms_accepted=True
    )


@pytest.fixture
def auth_client(user):
    """Authenticated API client"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client