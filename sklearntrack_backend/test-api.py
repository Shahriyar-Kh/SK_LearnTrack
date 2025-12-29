#!/usr/bin/env python3
# FILE: test_api.py
# Run with: python test_api.py
# ============================================================================

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{datetime.now().timestamp()}@example.com"
TEST_PASSWORD = "SecureTestPass123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}→ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_registration():
    """Test user registration endpoint"""
    print_info("\n1. Testing Registration...")
    
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
        "full_name": "Test User",
        "country": "USA",
        "education_level": "undergraduate",
        "field_of_study": "Computer Science",
        "learning_goal": "Learn everything",
        "preferred_study_hours": 3,
        "timezone": "UTC",
        "terms_accepted": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print_success(f"Registration successful for {TEST_EMAIL}")
            print_info(f"User role: {result['user']['role']}")
            
            if 'tokens' in result:
                print_success("Tokens received")
                return result['tokens']['access'], result['tokens']['refresh']
            else:
                print_error("Tokens not found in response")
                return None, None
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None, None

def test_login(email, password):
    """Test login endpoint"""
    print_info("\n2. Testing Login...")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Login successful for {email}")
            
            if 'user' in result:
                user = result['user']
                print_info(f"User role: {user.get('role', 'N/A')}")
                print_info(f"User email: {user.get('email', 'N/A')}")
                print_info(f"Redirect: {result.get('redirect', '/dashboard')}")
            
            if 'access' in result:
                print_success("Access token received")
                return result['access'], result.get('refresh', '')
            else:
                print_error("Access token not found in response")
                return None, None
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None, None

def test_get_current_user(access_token):
    """Test get current user endpoint"""
    print_info("\n3. Testing Get Current User...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/users/me/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            user = response.json()
            print_success("Got current user details")
            print_info(f"Email: {user.get('email', 'N/A')}")
            print_info(f"Full name: {user.get('full_name', 'N/A')}")
            print_info(f"Role: {user.get('role', 'N/A')}")
            print_info(f"Is staff: {user.get('is_staff', False)}")
            return True
        else:
            print_error(f"Get user failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Get user error: {str(e)}")
        return False

def test_token_refresh(refresh_token):
    """Test token refresh endpoint"""
    print_info("\n4. Testing Token Refresh...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/token/refresh/",
            json={"refresh": refresh_token},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Token refresh successful")
            if 'access' in result:
                print_success("New access token received")
                return result['access']
            else:
                print_error("Access token not found in response")
                return None
        else:
            print_error(f"Token refresh failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Token refresh error: {str(e)}")
        return None

def test_logout(refresh_token):
    """Test logout endpoint"""
    print_info("\n5. Testing Logout...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout/",
            json={"refresh": refresh_token},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("Logout successful")
            return True
        else:
            print_warning(f"Logout returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print_info("\n6. Testing Invalid Login...")
    
    data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400 or response.status_code == 401:
            print_success("Invalid login correctly rejected")
            return True
        else:
            print_error(f"Invalid login returned unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Invalid login test error: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  Django Authentication API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    print_info(f"\nBase URL: {BASE_URL}")
    print_info(f"Test email: {TEST_EMAIL}")
    
    # Test 1: Registration
    access_token, refresh_token = test_registration()
    if not access_token:
        print_error("\nRegistration failed. Stopping tests.")
        sys.exit(1)
    
    # Test 2: Login
    access_token, refresh_token = test_login(TEST_EMAIL, TEST_PASSWORD)
    if not access_token:
        print_error("\nLogin failed. Stopping tests.")
        sys.exit(1)
    
    # Test 3: Get current user
    test_get_current_user(access_token)
    
    # Test 4: Token refresh
    new_access_token = test_token_refresh(refresh_token)
    if new_access_token:
        access_token = new_access_token
    
    # Test 5: Logout
    test_logout(refresh_token)
    
    # Test 6: Invalid login
    test_invalid_login()
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}  All Tests Completed!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print_warning(f"Test user created: {TEST_EMAIL}")
    print_warning(f"Password: {TEST_PASSWORD}")
    print_info("You can use these credentials to test the frontend")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)