# FILE: profiles/views.py
# ============================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

from .models import Profile, NotificationSettings, ProfileActivityLog
from .serializers import (
    ProfileSerializer,
    NotificationSettingsSerializer,
    AvatarUploadSerializer,
    PreferencesSerializer,
    ChangePasswordSerializer,
    ActivitySummarySerializer,
    ActivityLogSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for user profile management
    
    Endpoints:
    - GET    /api/profile/              - Get current user's profile
    - PATCH  /api/profile/              - Update profile
    - POST   /api/profile/avatar/       - Upload avatar
    - GET    /api/profile/preferences/  - Get study preferences
    - PATCH  /api/profile/preferences/  - Update preferences
    - GET    /api/profile/notifications/ - Get notification settings
    - PATCH  /api/profile/notifications/ - Update notifications
    - POST   /api/profile/change-password/ - Change password
    - GET    /api/profile/activity/     - Get activity summary
    - GET    /api/profile/activity-log/ - Get activity log
    """
    
    permission_classes = [IsAuthenticated]
    
    def _get_user_profile(self, request):
        """Helper to get or create user profile"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        if created:
            logger.info(f"Created new profile for user: {request.user.email}")
        return profile
    
    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def list(self, request):
        """
        GET /api/profile/
        Get current user's complete profile
        """
        profile = self._get_user_profile(request)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    def partial_update(self, request):
        """
        PATCH /api/profile/
        Update profile fields
        """
        profile = self._get_user_profile(request)
        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated for user: {request.user.email}")
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def avatar(self, request):
        """
        POST /api/profile/avatar/
        Upload and update user avatar
        """
        profile = self._get_user_profile(request)
        serializer = AvatarUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Delete old avatar if exists
            if profile.avatar:
                old_avatar = profile.avatar
                profile.avatar = None
                profile.save()
                old_avatar.delete(save=False)
            
            # Save new avatar
            profile.avatar = serializer.validated_data['avatar']
            profile.save()
            
            # Log activity
            ProfileActivityLog.objects.create(
                profile=profile,
                activity_type='avatar_changed',
                description='Avatar updated',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f"Avatar updated for user: {request.user.email}")
            
            # Return avatar URL
            avatar_url = profile.get_avatar_url()
            if request:
                avatar_url = request.build_absolute_uri(avatar_url) if avatar_url else None
            
            return Response({
                'success': True,
                'message': 'Avatar uploaded successfully',
                'avatar': avatar_url
            })
            
        except Exception as e:
            logger.error(f"Avatar upload failed for {request.user.email}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to upload avatar',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get', 'patch'])
    def preferences(self, request):
        """
        GET/PATCH /api/profile/preferences/
        Get or update study preferences
        """
        profile = self._get_user_profile(request)
        
        if request.method == 'GET':
            serializer = PreferencesSerializer(profile)
            return Response(serializer.data)
        
        # PATCH
        serializer = PreferencesSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Preferences updated for user: {request.user.email}")
            return Response({
                'success': True,
                'message': 'Preferences updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'patch'])
    def notifications(self, request):
        """
        GET/PATCH /api/profile/notifications/
        Get or update notification settings
        """
        profile = self._get_user_profile(request)
        
        # Get or create notification settings
        notification_settings, created = NotificationSettings.objects.get_or_create(
            profile=profile
        )
        
        if request.method == 'GET':
            serializer = NotificationSettingsSerializer(notification_settings)
            return Response(serializer.data)
        
        # PATCH
        serializer = NotificationSettingsSerializer(
            notification_settings,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Notification settings updated for user: {request.user.email}")
            return Response({
                'success': True,
                'message': 'Notification settings updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        POST /api/profile/change-password/
        Change user password
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update password
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log activity
            profile = self._get_user_profile(request)
            ProfileActivityLog.objects.create(
                profile=profile,
                activity_type='password_changed',
                description='Password changed successfully',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f"Password changed for user: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Password changed successfully. Please login again with your new password.'
            })
            
        except Exception as e:
            logger.error(f"Password change failed for {request.user.email}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to change password'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """
        GET /api/profile/activity/
        Get account activity summary
        """
        user = request.user
        profile = self._get_user_profile(request)
        
        # Get active courses count (enrollments not completed)
        enrollments_count = 0
        if hasattr(user, 'enrollments'):
            enrollments_count = user.enrollments.filter(completed_at__isnull=True).count()
        
        summary_data = {
            'totalStudyDays': profile.total_study_days,
            'totalNotes': profile.total_notes,
            'activeCourses': enrollments_count,
            'currentStreak': profile.current_streak,
            'longestStreak': profile.longest_streak,
            'lastLogin': user.last_login_at or user.created_at,
            'accountCreated': user.created_at,
            'emailVerified': user.email_verified,
        }
        
        serializer = ActivitySummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='delete-avatar')
    def delete_avatar(self, request):
        """
        DELETE /api/profile/delete-avatar/
        Remove user avatar
        """
        profile = self._get_user_profile(request)
        
        if not profile.avatar:
            return Response({
                'success': False,
                'error': 'No avatar to delete'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Delete avatar file
            avatar = profile.avatar
            profile.avatar = None
            profile.save()
            avatar.delete(save=False)
            
            # Log activity
            ProfileActivityLog.objects.create(
                profile=profile,
                activity_type='avatar_changed',
                description='Avatar removed',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f"Avatar deleted for user: {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Avatar deleted successfully'
            })
            
        except Exception as e:
            logger.error(f"Avatar deletion failed for {request.user.email}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to delete avatar'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)