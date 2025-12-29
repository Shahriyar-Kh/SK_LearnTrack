# FILE: tests/test_auth.py
# ============================================================================

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        email = kwargs.pop('email', f'test_{uuid.uuid4()}@example.com')
        password = kwargs.pop('password', 'SecurePass123!')
        
        # Use create_user which doesn't require username
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=kwargs.pop('full_name', 'Test User'),
            country=kwargs.pop('country', 'USA'),
            education_level=kwargs.pop('education_level', 'undergraduate'),
            field_of_study=kwargs.pop('field_of_study', 'Computer Science'),
            terms_accepted=kwargs.pop('terms_accepted', True),
            **kwargs
        )
        return user
    return make_user


@pytest.fixture
def user(create_user):
    return create_user()


@pytest.fixture
def authenticated_user(user):
    """Create a user and get auth tokens"""
    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }


@pytest.mark.django_db
class TestRegistration:
    """Test user registration endpoints"""
    
    def test_register_success(self, api_client):
        """Test successful user registration"""
        email = f'test_{uuid.uuid4()}@example.com'
        response = api_client.post("/api/auth/register/", {
            "email": email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "New User",
            "country": "PK",
            "education_level": "undergraduate",
            "field_of_study": "Computer Science",
            "terms_accepted": True
        }, format='json')
        
        assert response.status_code == 201
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        assert response.data['user']['email'] == email
        assert response.data['user']['full_name'] == "New User"
        assert response.data['user']['role'] == 'student'
    
    def test_register_missing_required_field(self, api_client):
        """Test registration with missing required field"""
        response = api_client.post("/api/auth/register/", {
            "email": f'test_{uuid.uuid4()}@example.com',
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Test User",
            "country": "PK",
            "education_level": "undergraduate",
            # Missing field_of_study
            "terms_accepted": True
        }, format='json')
        
        assert response.status_code == 400
        assert 'field_of_study' in response.data
    
    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords"""
        response = api_client.post("/api/auth/register/", {
            "email": f'test_{uuid.uuid4()}@example.com',
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass456!",
            "full_name": "Test User",
            "country": "PK",
            "education_level": "undergraduate",
            "field_of_study": "CS",
            "terms_accepted": True
        }, format='json')
        
        assert response.status_code == 400
        # Check for either 'password' or 'password_confirm' in response
        assert 'password_confirm' in response.data or 'password' in response.data
    
    def test_register_weak_password(self, api_client):
        """Test registration with weak password"""
        response = api_client.post("/api/auth/register/", {
            "email": f'test_{uuid.uuid4()}@example.com',
            "password": "123",
            "password_confirm": "123",
            "full_name": "Test User",
            "country": "PK",
            "education_level": "undergraduate",
            "field_of_study": "CS",
            "terms_accepted": True
        }, format='json')
        
        assert response.status_code == 400
        assert 'password' in response.data
    
    def test_register_terms_not_accepted(self, api_client):
        """Test registration without accepting terms"""
        response = api_client.post("/api/auth/register/", {
            "email": f'test_{uuid.uuid4()}@example.com',
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Test User",
            "country": "PK",
            "education_level": "undergraduate",
            "field_of_study": "CS",
            "terms_accepted": False
        }, format='json')
        
        assert response.status_code == 400
        assert 'terms_accepted' in response.data
    
    def test_register_duplicate_email(self, api_client, user):
        """Test registration with duplicate email"""
        response = api_client.post("/api/auth/register/", {
            "email": user.email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Test User",
            "country": "PK",
            "education_level": "undergraduate",
            "field_of_study": "CS",
            "terms_accepted": True
        }, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data


@pytest.mark.django_db
class TestLogin:
    """Test user login endpoints"""
    
    def test_login_success(self, api_client, user):
        """Test successful login"""
        response = api_client.post("/api/token/", {
            "email": user.email,
            "password": "SecurePass123!"
        }, format='json')
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == user.email
    
    def test_login_wrong_password(self, api_client, user):
        """Test login with wrong password"""
        response = api_client.post("/api/token/", {
            "email": user.email,
            "password": "WrongPassword123!"
        }, format='json')
        
        assert response.status_code == 400
        assert 'detail' in response.data
    
    def test_login_nonexistent_email(self, api_client):
        """Test login with non-existent email"""
        response = api_client.post("/api/token/", {
            "email": "nonexistent@example.com",
            "password": "SecurePass123!"
        }, format='json')
        
        assert response.status_code == 400
        assert 'detail' in response.data
    
    def test_login_missing_credentials(self, api_client):
        """Test login with missing credentials"""
        response = api_client.post("/api/token/", {
            "email": "",
            "password": ""
        }, format='json')
        
        assert response.status_code == 400
        # Can be either 'detail' or field-specific errors
        assert 'detail' in response.data or 'email' in response.data or 'password' in response.data


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint"""
    
    def test_token_refresh_success(self, api_client, authenticated_user):
        """Test successful token refresh"""
        response = api_client.post("/api/token/refresh/", {
            "refresh": authenticated_user['refresh_token']
        }, format='json')
        
        assert response.status_code == 200
        assert 'access' in response.data
    
    def test_token_refresh_invalid(self, api_client):
        """Test token refresh with invalid refresh token"""
        response = api_client.post("/api/token/refresh/", {
            "refresh": "invalid.refresh.token"
        }, format='json')
        
        assert response.status_code == 401
        assert 'detail' in response.data


@pytest.mark.django_db
class TestCurrentUser:
    """Test current user endpoints"""
    
    def test_get_current_user_authenticated(self, api_client, authenticated_user):
        """Test getting current user with authentication"""
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {authenticated_user["access_token"]}'
        )
        response = api_client.get("/api/auth/users/me/")
        
        assert response.status_code == 200
        assert response.data['email'] == authenticated_user['user'].email
        assert response.data['full_name'] == authenticated_user['user'].full_name
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user without authentication"""
        response = api_client.get("/api/auth/users/me/")
        
        assert response.status_code == 401
        assert 'detail' in response.data
    
    def test_update_profile(self, api_client, authenticated_user):
        """Test updating user profile"""
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {authenticated_user["access_token"]}'
        )
        
        new_bio = "Updated bio from test"
        response = api_client.put("/api/auth/users/update_profile/", {
            "bio": new_bio,
            "email_notifications": False
        }, format='json')
        
        assert response.status_code == 200
        assert response.data['bio'] == new_bio
        
        # Verify the update
        user_response = api_client.get("/api/auth/users/me/")
        assert user_response.data['profile']['bio'] == new_bio


@pytest.mark.django_db
class TestLogout:
    """Test logout endpoint"""
    
    def test_logout_success(self, api_client, authenticated_user):
        """Test successful logout"""
        response = api_client.post("/api/auth/logout/", {
            "refresh": authenticated_user['refresh_token']
        }, format='json')
        
        assert response.status_code == 200
        assert 'message' in response.data
    
    def test_logout_invalid_token(self, api_client):
        """Test logout with invalid token"""
        response = api_client.post("/api/auth/logout/", {
            "refresh": "invalid.refresh.token"
        }, format='json')
        
        assert response.status_code == 400
        assert 'error' in response.data


@pytest.mark.django_db
class TestUserModel:
    """Test User model methods"""
    
    def test_user_creation(self):
        """Test user creation with auto-generated username"""
        email = f"test_{uuid.uuid4()}@example.com"
        user = User.objects.create_user(
            email=email,
            password="TestPass123",
            full_name="Test User",
            country="USA",
            education_level="undergraduate",
            field_of_study="CS",
            terms_accepted=True
        )
        
        assert user.email == email
        assert user.check_password("TestPass123")
        assert user.username is not None
        assert user.username.startswith(email.split('@')[0])
        assert user.role == 'student'
        # Profile should be created by signal
        assert hasattr(user, 'profile')
    
    def test_user_str_representation(self, user):
        """Test user string representation"""
        assert str(user) == user.email
    
    def test_auto_username_generation(self):
        """Test auto username generation for duplicate emails"""
        base_username = "testuser"
        
        # Create first user
        user1 = User.objects.create_user(
            email=f"{base_username}@example.com",
            password="TestPass123",
            full_name="User 1",
            country="USA",
            education_level="undergraduate",
            field_of_study="CS",
            terms_accepted=True
        )
        
        # Create second user with different email but same base username
        user2 = User.objects.create_user(
            email=f"{base_username}2@example.com",
            password="TestPass123",
            full_name="User 2",
            country="USA",
            education_level="undergraduate",
            field_of_study="CS",
            terms_accepted=True
        )
        
        assert user1.username != user2.username
        assert user1.username == base_username
        assert user2.username == f"{base_username}2"


@pytest.mark.django_db
class TestProfileModel:
    """Test Profile model"""
    
    def test_profile_auto_creation(self, user):
        """Test profile is automatically created with user"""
        assert hasattr(user, 'profile')
        assert user.profile is not None
    
    def test_profile_str_representation(self, user):
        """Test profile string representation"""
        assert str(user.profile) == f"{user.email}'s Profile"
    
    def test_profile_default_values(self, user):
        """Test profile default values"""
        profile = user.profile
        assert profile.email_notifications == True
        assert profile.weekly_summary == True
        assert profile.course_reminders == True
        assert profile.total_study_days == 0
        assert profile.current_streak == 0
        assert profile.longest_streak == 0


@pytest.mark.django_db
def test_register_and_login_workflow(api_client):
    """Test complete registration and login workflow"""
    # Step 1: Register
    email = f"workflow_{uuid.uuid4()}@example.com"
    register_response = api_client.post("/api/auth/register/", {
        "email": email,
        "password": "WorkflowPass123!",
        "password_confirm": "WorkflowPass123!",
        "full_name": "Workflow User",
        "country": "CA",
        "education_level": "graduate",
        "field_of_study": "Data Science",
        "terms_accepted": True
    }, format='json')
    
    assert register_response.status_code == 201
    assert 'tokens' in register_response.data
    
    # Step 2: Login with same credentials
    login_response = api_client.post("/api/token/", {
        "email": email,
        "password": "WorkflowPass123!"
    }, format='json')
    
    assert login_response.status_code == 200
    assert 'access' in login_response.data
    
    # Step 3: Get current user
    access_token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    me_response = api_client.get("/api/auth/users/me/")
    
    assert me_response.status_code == 200
    assert me_response.data['email'] == email
    assert me_response.data['full_name'] == "Workflow User"
    
    # Step 4: Logout
    refresh_token = login_response.data['refresh']
    logout_response = api_client.post("/api/auth/logout/", {
        "refresh": refresh_token
    }, format='json')
    
    assert logout_response.status_code == 200


@pytest.mark.django_db
def test_invalid_endpoints(api_client):
    """Test invalid endpoints return appropriate errors"""
    # Test non-existent endpoint
    response = api_client.get("/api/nonexistent/")
    assert response.status_code == 404
    
    # Test wrong method
    response = api_client.get("/api/auth/register/")
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.django_db
def test_superuser_creation():
    """Test superuser creation"""
    email = f"admin_{uuid.uuid4()}@example.com"
    user = User.objects.create_superuser(
        email=email,
        password="AdminPass123!",
        full_name="Admin User"
    )
    
    assert user.is_superuser == True
    assert user.is_staff == True
    assert user.role == 'admin'
    assert user.email == email