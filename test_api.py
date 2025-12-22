import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Register a new user
def test_register():
    url = f"{BASE_URL}/auth/register/"
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Test User",
        "country": "United States",
        "education_level": "undergraduate",
        "field_of_study": "Computer Science",
        "learning_goal": "Master full-stack development",
        "preferred_study_hours": 3,
        "timezone": "America/New_York",
        "terms_accepted": True
    }
    
    response = requests.post(url, json=data)
    print("Registration Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

# 2. Login
def test_login():
    url = f"{BASE_URL}/token/"
    data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    response = requests.post(url, json=data)
    print("\nLogin Response:", response.status_code)
    tokens = response.json()
    print(json.dumps(tokens, indent=2))
    return tokens

# 3. Get current user profile
def test_get_profile(access_token):
    url = f"{BASE_URL}/auth/users/me/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print("\nProfile Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

# 4. Get courses
def test_get_courses(access_token):
    url = f"{BASE_URL}/courses/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print("\nCourses Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

# Run tests
if __name__ == "__main__":
    print("=" * 50)
    print("API Testing Started")
    print("=" * 50)
    
    # Register
    registration = test_register()
    
    # Login
    tokens = test_login()
    access_token = tokens.get('access')
    
    # Get profile
    test_get_profile(access_token)
    
    # Get courses
    test_get_courses(access_token)
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)