# FILE: profiles/tests.py
# ============================================================================

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from .models import Profile, NotificationSettings, ProfileActivityLog

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test Profile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            country='USA',
            education_level='undergraduate',
            field_of_study='Computer Science',
            terms_accepted=True
        )
    
    def test_profile_auto_created(self):
        """Test profile is automatically created for new users"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
    
    def test_profile_default_values(self):
        """Test profile default values"""
        profile = self.user.profile
        self.assertEqual(profile.preferred_study_hours, 2)
        self.assertEqual(profile.timezone, 'UTC')
        self.assertEqual(profile.total_study_days, 0)
        self.assertEqual(profile.skill_interests, [])
    
    def test_add_skill_interest(self):
        """Test adding skill interest"""
        profile = self.user.profile
        profile.add_skill_interest('Python')
        self.assertIn('Python', profile.skill_interests)
        
        # Test duplicate prevention
        profile.add_skill_interest('Python')
        self.assertEqual(profile.skill_interests.count('Python'), 1)
    
    def test_remove_skill_interest(self):
        """Test removing skill interest"""
        profile = self.user.profile
        profile.skill_interests = ['Python', 'Django']
        profile.save()
        
        profile.remove_skill_interest('Python')
        self.assertNotIn('Python', profile.skill_interests)
        self.assertIn('Django', profile.skill_interests)


class ProfileAPITest(APITestCase):
    """Test Profile API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            country='USA',
            education_level='undergraduate',
            field_of_study='Computer Science',
            terms_accepted=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        """Test GET /api/profile/"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['fullName'], 'Test User')
    
    def test_update_profile(self):
        """Test PATCH /api/profile/"""
        data = {
            'fullName': 'Updated Name',
            'bio': 'Updated bio',
            'preferredStudyHours': 4
        }
        response = self.client.patch('/api/profile/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        self.assertEqual(self.user.profile.bio, 'Updated bio')
        self.assertEqual(self.user.profile.preferred_study_hours, 4)
    
    def test_update_profile_validation(self):
        """Test profile update validation"""
        # Test invalid study hours
        data = {'preferredStudyHours': 15}
        response = self.client.patch('/api/profile/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test bio too long
        data = {'bio': 'x' * 2001}
        response = self.client.patch('/api/profile/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_upload_avatar(self):
        """Test POST /api/profile/avatar/"""
        # Create test image
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        avatar = SimpleUploadedFile(
            'test_avatar.jpg',
            image_io.read(),
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            '/api/profile/avatar/',
            {'avatar': avatar},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['avatar'])
        
        # Verify avatar saved
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.avatar)
    
    def test_get_preferences(self):
        """Test GET /api/profile/preferences/"""
        response = self.client.get('/api/profile/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('learningGoal', response.data)
        self.assertIn('preferredStudyHours', response.data)
    
    def test_update_preferences(self):
        """Test PATCH /api/profile/preferences/"""
        data = {
            'learningGoal': 'Master Django',
            'preferredStudyHours': 5,
            'timezone': 'America/New_York',
            'skillInterests': ['Python', 'Django', 'React']
        }
        response = self.client.patch('/api/profile/preferences/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify changes
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.learning_goal, 'Master Django')
        self.assertEqual(len(self.user.profile.skill_interests), 3)
    
    def test_get_notifications(self):
        """Test GET /api/profile/notifications/"""
        response = self.client.get('/api/profile/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email_notifications', response.data)
    
    def test_update_notifications(self):
        """Test PATCH /api/profile/notifications/"""
        data = {
            'email_notifications': False,
            'weekly_summary': False
        }
        response = self.client.patch('/api/profile/notifications/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_change_password(self):
        """Test POST /api/profile/change-password/"""
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!'
        }
        response = self.client.post('/api/profile/change-password/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))
    
    def test_change_password_wrong_old(self):
        """Test password change with wrong current password"""
        data = {
            'old_password': 'WrongPass123!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!'
        }
        response = self.client.post('/api/profile/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_activity_summary(self):
        """Test GET /api/profile/activity/"""
        response = self.client.get('/api/profile/activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalStudyDays', response.data)
        self.assertIn('totalNotes', response.data)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access profile"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NotificationSettingsTest(TestCase):
    """Test NotificationSettings model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            country='USA',
            education_level='undergraduate',
            field_of_study='Computer Science',
            terms_accepted=True
        )
    
    def test_notification_settings_auto_created(self):
        """Test notification settings auto-created with profile"""
        self.assertTrue(hasattr(self.user.profile, 'notification_settings'))
        settings = self.user.profile.notification_settings
        self.assertTrue(settings.email_notifications)
        self.assertTrue(settings.weekly_summary)


class ActivityLogTest(TestCase):
    """Test ProfileActivityLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            full_name='Test User',
            country='USA',
            education_level='undergraduate',
            field_of_study='Computer Science',
            terms_accepted=True
        )
    
    def test_create_activity_log(self):
        """Test creating activity log"""
        log = ProfileActivityLog.objects.create(
            profile=self.user.profile,
            activity_type='profile_updated',
            description='Profile info updated',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(log.profile, self.user.profile)
        self.assertEqual(log.activity_type, 'profile_updated')
        self.assertIsNotNone(log.created_at)