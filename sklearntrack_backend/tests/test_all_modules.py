#!/usr/bin/env python3
# FILE: test_all_modules.py
# Run with: python test_all_modules.py
# ============================================================================

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}→ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

# Global variables for test data
test_email = f"test_{int(datetime.now().timestamp())}@example.com"
test_password = "TestPass123!"
access_token = None
refresh_token = None
user_data = None
note_id = None
chapter_id = None
topic_id = None

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_registration():
    """Test user registration"""
    print_info("Testing Registration...")
    
    data = {
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password,
        "full_name": "Test User",
        "country": "USA",
        "education_level": "undergraduate",
        "field_of_study": "Computer Science",
        "learning_goal": "Master Django",
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
            print_success(f"Registration successful: {test_email}")
            
            global access_token, refresh_token, user_data
            if 'tokens' in result:
                access_token = result['tokens']['access']
                refresh_token = result['tokens']['refresh']
                user_data = result['user']
                print_info(f"User ID: {user_data['id']}")
                print_info(f"Role: {user_data['role']}")
                return True
            else:
                print_error("Tokens not found in response")
                return False
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return False

def test_login():
    """Test login"""
    print_info("Testing Login...")
    
    data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Login successful")
            
            global access_token, refresh_token
            access_token = result['access']
            refresh_token = result['refresh']
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False

def test_get_current_user():
    """Test get current user"""
    print_info("Testing Get Current User...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/users/me/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            user = response.json()
            print_success("Retrieved user details")
            print_info(f"Email: {user['email']}")
            print_info(f"Full name: {user['full_name']}")
            return True
        else:
            print_error(f"Get user failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get user error: {str(e)}")
        return False

# ============================================================================
# NOTES MODULE TESTS
# ============================================================================

def test_create_note():
    """Test creating a note"""
    print_info("Testing Create Note...")
    
    data = {
        "title": "Test Note",
        "status": "draft",
        "tags": ["test", "api"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/notes/",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            global note_id
            note_id = result['id']
            print_success(f"Note created: ID {note_id}")
            return True
        else:
            print_error(f"Create note failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Create note error: {str(e)}")
        return False

def test_create_chapter():
    """Test creating a chapter"""
    print_info("Testing Create Chapter...")
    
    data = {
        "note_id": note_id,
        "title": "Test Chapter"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chapters/",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            global chapter_id
            chapter_id = result['id']
            print_success(f"Chapter created: ID {chapter_id}")
            return True
        else:
            print_error(f"Create chapter failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Create chapter error: {str(e)}")
        return False

def test_create_topic():
    """Test creating a topic"""
    print_info("Testing Create Topic...")
    
    data = {
        "chapter_id": chapter_id,
        "name": "Test Topic",
        "explanation_content": "This is a test explanation",
        "code_language": "python",
        "code_content": "print('Hello, World!')",
        "source_title": "Python Docs",
        "source_url": "https://docs.python.org"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/topics/",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
            result = response.json()
            global topic_id
            topic_id = result['id']
            print_success(f"Topic created: ID {topic_id}")
            print_info(f"Has explanation: {result['has_explanation']}")
            print_info(f"Has code: {result['has_code']}")
            print_info(f"Has source: {result['has_source']}")
            return True
        else:
            print_error(f"Create topic failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Create topic error: {str(e)}")
        return False

def test_update_topic():
    """Test updating a topic"""
    print_info("Testing Update Topic...")
    
    data = {
        "name": "Updated Test Topic",
        "explanation_content": "This is an updated explanation"
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/api/topics/{topic_id}/",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Topic updated successfully")
            return True
        else:
            print_error(f"Update topic failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Update topic error: {str(e)}")
        return False

def test_get_note_structure():
    """Test getting note structure"""
    print_info("Testing Get Note Structure...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/notes/{note_id}/structure/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Retrieved note structure")
            print_info(f"Note title: {result['title']}")
            print_info(f"Chapters: {len(result['chapters'])}")
            if result['chapters']:
                print_info(f"Topics in first chapter: {len(result['chapters'][0]['topics'])}")
            return True
        else:
            print_error(f"Get structure failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get structure error: {str(e)}")
        return False

def test_list_notes():
    """Test listing notes"""
    print_info("Testing List Notes...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/notes/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Retrieved {len(result)} notes")
            return True
        else:
            print_error(f"List notes failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List notes error: {str(e)}")
        return False

# ============================================================================
# COURSES MODULE TESTS
# ============================================================================

def test_list_courses():
    """Test listing courses"""
    print_info("Testing List Courses...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/courses/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Retrieved courses")
            return True
        else:
            print_error(f"List courses failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List courses error: {str(e)}")
        return False

def test_get_enrollments():
    """Test getting enrollments"""
    print_info("Testing Get Enrollments...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/courses/enrollments/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Retrieved enrollments")
            return True
        else:
            print_error(f"Get enrollments failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get enrollments error: {str(e)}")
        return False

# ============================================================================
# ANALYTICS MODULE TESTS
# ============================================================================

def test_dashboard_analytics():
    """Test dashboard analytics"""
    print_info("Testing Dashboard Analytics...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/dashboard/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Retrieved dashboard analytics")
            print_info(f"Weekly study time: {result.get('weekly_study_time', 0)} min")
            print_info(f"Current streak: {result.get('current_streak', 0)} days")
            return True
        else:
            print_error(f"Dashboard analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Dashboard analytics error: {str(e)}")
        return False

# ============================================================================
# ROADMAPS MODULE TESTS
# ============================================================================

def test_list_roadmaps():
    """Test listing roadmaps"""
    print_info("Testing List Roadmaps...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/roadmaps/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Retrieved roadmaps")
            return True
        else:
            print_error(f"List roadmaps failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List roadmaps error: {str(e)}")
        return False

# ============================================================================
# CLEANUP
# ============================================================================

def cleanup():
    """Delete test data"""
    print_info("Cleaning up test data...")
    
    # Delete note (cascades to chapters and topics)
    if note_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/api/notes/{note_id}/",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code in [200, 204]:
                print_success("Test note deleted")
            else:
                print_warning(f"Could not delete note: {response.status_code}")
        except Exception as e:
            print_warning(f"Cleanup error: {str(e)}")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print_header("SK-LEARNTRACK API COMPREHENSIVE TEST SUITE")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    tests = [
        # Authentication
        ("Registration", test_registration),
        ("Login", test_login),
        ("Get Current User", test_get_current_user),
        
        # Notes Module
        ("Create Note", test_create_note),
        ("Create Chapter", test_create_chapter),
        ("Create Topic", test_create_topic),
        ("Update Topic", test_update_topic),
        ("Get Note Structure", test_get_note_structure),
        ("List Notes", test_list_notes),
        
        # Courses Module
        ("List Courses", test_list_courses),
        ("Get Enrollments", test_get_enrollments),
        
        # Analytics Module
        ("Dashboard Analytics", test_dashboard_analytics),
        
        # Roadmaps Module
        ("List Roadmaps", test_list_roadmaps),
    ]
    
    for test_name, test_func in tests:
        results['total'] += 1
        print_header(f"TEST: {test_name}")
        
        try:
            if test_func():
                results['passed'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            results['failed'] += 1
    
    # Cleanup
    print_header("CLEANUP")
    cleanup()
    
    # Results
    print_header("TEST RESULTS")
    print(f"\n{Colors.CYAN}Total Tests: {results['total']}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    success_rate = (results['passed'] / results['total']) * 100
    print(f"\n{Colors.BLUE}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! Your API is working perfectly!{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{'='*70}{Colors.END}")
        print(f"{Colors.RED}❌ Some tests failed. Please review the errors above.{Colors.END}")
        print(f"{Colors.RED}{'='*70}{Colors.END}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(run_all_tests())
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print_error(f"\nFatal error: {str(e)}")
        sys.exit(1)