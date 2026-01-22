# FILE: accounts/views.py - FIXED GOOGLE OAUTH
# ============================================================================

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail

# Add these imports at the top
import threading
import requests
import json


from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uuid
import logging
from datetime import timedelta
import socket  # ADD THIS IMPORT
import urllib.parse  # ADD THIS IMPORT

from .models import LoginActivity, PasswordReset, EmailVerification
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    LoginActivitySerializer, EmailTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    GoogleAuthSerializer, ProfileUpdateSerializer
)
from .permissions import IsAdminUser

User = get_user_model()
logger = logging.getLogger(__name__)


# ==================== EMAIL HELPER FUNCTIONS ====================
def send_email_sync(subject, message, from_email, recipient_list):
    """
    ✅ FIXED: Synchronous email sending with proper error handling
    Use this in production to ensure emails are sent before response
    """
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,  # ✅ CRITICAL: Don't hide errors!
        )
        
        if result == 1:
            logger.info(f"✅ Email sent successfully to: {recipient_list}")
            return True
        else:
            logger.error(f"❌ Email failed to send to: {recipient_list}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Email sending error: {str(e)}")
        logger.error(f"❌ Recipients: {recipient_list}")
        logger.error(f"❌ Subject: {subject}")
        # Log the full exception for debugging
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return False


def send_email_safe(subject, message, from_email, recipient_list):
    """
    ✅ SAFE VERSION: Tries to send email but doesn't crash if it fails
    Returns success status
    """
    try:
        return send_email_sync(subject, message, from_email, recipient_list)
    except Exception as e:
        logger.error(f"❌ Email system failure: {str(e)}")
        return False

class AuthViewSet(viewsets.GenericViewSet):
    """
    Enhanced authentication endpoints with improved structure,
    consistent error handling, and security best practices.
    """
    
    permission_classes = [permissions.AllowAny]
    
    # ==================== REGISTRATION ====================
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user with email verification and automatic login.
        Returns JWT tokens upon successful registration.
        """
        logger.info(f"Registration attempt for email: {request.data.get('email', 'N/A')}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create user
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
            
            # Send verification email (non-blocking)
            try:
                self._send_verification_email(user, request)
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                # Continue registration even if email fails
            
            # Generate JWT tokens with user claims
            refresh = RefreshToken.for_user(user)
            self._add_user_claims(refresh, user)
            
            # Track login activity
            self._track_login_activity(request, user)
            
            response_data = {
                'success': True,
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': '/dashboard',
                'message': 'Registration successful! Please check your email to verify your account.',
                'requires_verification': not user.email_verified
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration failed unexpectedly: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Registration failed due to server error',
                'detail': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== GOOGLE OAUTH ====================
    @action(detail=False, methods=['post'])
    def google_auth(self, request):
        """
        Authenticate with Google OAuth.
        Creates new user or links Google account to existing user.
        """
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = serializer.validated_data['credential']
            
            # Validate Google configuration
            google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            if not google_client_id or 'your-google-client-id' in google_client_id:
                logger.error("Google OAuth Client ID is not properly configured")
                return Response({
                    'success': False,
                    'error': 'Google OAuth is not configured on the server',
                    'detail': 'Please contact the administrator'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                google_client_id
            )
            
            # Validate token issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            # Extract user info
            email = idinfo.get('email')
            google_id = idinfo.get('sub')
            full_name = idinfo.get('name', '')
            email_verified = idinfo.get('email_verified', False)
            
            if not email:
                return Response({
                    'success': False,
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find or create user
            user, created = self._get_or_create_google_user(
                email=email,
                google_id=google_id,
                full_name=full_name,
                email_verified=email_verified
            )
            
            if not user.is_active:
                return Response({
                    'success': False,
                    'error': 'User account is disabled'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            self._add_user_claims(refresh, user)
            
            # Update login tracking
            self._track_login_activity(request, user)
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            # Determine redirect URL based on role
            redirect_url = '/admin-dashboard' if user.role == 'admin' or user.is_staff else '/dashboard'
            
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': redirect_url,
                'is_new_user': created,
                'message': 'Google authentication successful'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            error_msg = str(e)
            logger.warning(f"Google token validation failed: {error_msg}")
            
            # 🔒 SECURITY FIX: Do not expose client IDs in error messages
            if "wrong audience" in error_msg.lower() or "audience" in error_msg.lower():
                return Response({
                    'success': False,
                    'error': 'Invalid Google token',
                    'detail': 'Google authentication failed. Please try again or use email login.',
                    'error_type': 'google_auth_failed'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid Google token',
                    'detail': 'Google authentication failed. Please try again.',
                    'error_type': 'google_auth_failed'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Google authentication failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Google authentication failed',
                'detail': 'Please try again',
                'error_type': 'google_auth_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== PASSWORD RESET ====================
    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        """
        Request password reset email.
        Security: Always returns success to prevent email enumeration.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email'].lower().strip()
        
        try:
            user = User.objects.get(email=email)
            
            # Create reset token (expires in 1 hour)
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=1)
            
            PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Send reset email
            try:
                self._send_password_reset_email(user, token)
                logger.info(f"Password reset email sent to: {email}")
            except Exception as e:
                logger.error(f"Failed to send reset email to {email}: {str(e)}")
                # Continue silently - security best practice
            
        except User.DoesNotExist:
            # Security: Don't reveal that email doesn't exist
            logger.info(f"Password reset requested for non-existent email: {email}")
        
        # Always return the same success message
        return Response({
            'success': True,
            'message': 'If an account exists with this email, you will receive a password reset link.',
            'instructions': 'Check your inbox and spam folder. Link expires in 1 hour.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """
        Reset password using valid token.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset = PasswordReset.objects.get(token=token)
            
            if not reset.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update password
            user = reset.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset.used = True
            reset.save()
            
            logger.info(f"Password reset successful for: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Password reset successful. You can now login with your new password.',
                'next_action': 'Proceed to login page'
            }, status=status.HTTP_200_OK)
            
        except PasswordReset.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # ==================== EMAIL VERIFICATION ====================
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """
        Verify email address using verification token.
        """
        token = request.data.get('token')
        
        if not token:
            return Response({
                'success': False,
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification = EmailVerification.objects.get(token=token)
            
            if not verification.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid or expired verification token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark email as verified
            user = verification.user
            user.email_verified = True
            user.save()
            
            verification.verified = True
            verification.save()
            
            logger.info(f"Email verified for user: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Email verified successfully!',
                'user_email': user.email
            }, status=status.HTTP_200_OK)
            
        except EmailVerification.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        """
        Resend email verification link.
        """
        email = request.data.get('email', '').lower().strip()
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                return Response({
                    'success': True,
                    'message': 'Email is already verified'
                }, status=status.HTTP_200_OK)
            
            # Send new verification email
            self._send_verification_email(user, request)
            
            return Response({
                'success': True,
                'message': 'Verification email sent',
                'instructions': 'Check your inbox and spam folder.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Security: Don't reveal if email exists
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a verification link will be sent.'
            }, status=status.HTTP_200_OK)
    
    # ==================== LOGOUT ====================
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout user and blacklist refresh token.
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"User logged out (token blacklisted)")
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"Logout failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # ==================== HELPER METHODS ====================
    def _get_or_create_google_user(self, email, google_id, full_name, email_verified):
        """
        Find existing user by Google ID or email, or create new user.
        Returns tuple of (user, created_flag)
        """
        user = None
        created = False
        
        # Try to find by Google ID first
        if google_id:
            try:
                user = User.objects.get(google_id=google_id)
                return user, False
            except User.DoesNotExist:
                pass
        
        # Try to find by email
        try:
            user = User.objects.get(email=email)
            # Link Google account to existing user
            if not user.google_id:
                user.google_id = google_id
            if not user.email_verified:
                user.email_verified = email_verified
            user.save()
            return user, False
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                email=email,
                google_id=google_id,
                full_name=full_name,
                email_verified=email_verified,
                terms_accepted=True,
                role='student',
            )
            return user, True
    
    def _send_password_reset_email(self, user, token):
        """
        ✅ FIXED: Send password reset email synchronously with error handling
        """
        frontend_url = settings.FRONTEND_URL
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        subject = 'Reset Your SK-LearnTrack Password'
        message = f"""Hello {user.full_name or user.email},

You requested to reset your password for your SK-LearnTrack account.

Click the link below to set a new password (valid for 1 hour):
{reset_url}

If you did not request this password reset, please ignore this email.
Your account security is important to us.

Best regards,
SK-LearnTrack Team
"""
        
        # ✅ FIXED: Use synchronous sending with proper error handling
        success = send_email_sync(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        
        if success:
            logger.info(f"✅ Password reset email sent to {user.email}")
        else:
            logger.error(f"❌ Failed to send password reset email to {user.email}")
        
        return success

    def _send_verification_email(self, user, request):
        """
        ✅ FIXED: Send email verification link synchronously
        """
        # Create verification token (expires in 7 days)
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)
        
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Build verification URL
        frontend_url = settings.FRONTEND_URL
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        subject = 'Verify Your SK-LearnTrack Account'
        message = f"""Welcome to SK-LearnTrack!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 7 days.

If you did not create an account, please ignore this email.

Thank you,
SK-LearnTrack Team
"""
        
        # ✅ FIXED: Use synchronous sending
        success = send_email_sync(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        
        if success:
            logger.info(f"✅ Verification email sent to {user.email}")
        else:
            logger.error(f"❌ Failed to send verification email to {user.email}")
        
        return success
        
    def _track_login_activity(self, request, user):
        """
        Record user login activity for security monitoring.
        """
        try:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            
            LoginActivity.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Failed to track login activity: {str(e)}")
    
    def _get_client_ip(self, request):
        """
        Extract client IP address from request headers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def _add_user_claims(self, token, user):
        """
        Add custom claims to JWT token.
        """
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['user_id'] = str(user.id)
        
        # ✅ FIXED: Safe profile completeness check
        profile_complete = False
        try:
            if hasattr(user, 'profile') and user.profile:
                # Check if profile has an avatar (simple completeness check)
                if hasattr(user.profile, 'avatar'):
                    profile_complete = bool(user.profile.avatar)
        except Exception as e:
            # Log but don't crash
            logger.debug(f"Profile completeness check failed for {user.email}: {str(e)}")
        
        token['profile_complete'] = profile_complete

class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Admin-only actions"""
        if self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old and new passwords are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        })
    
    @action(detail=False, methods=['get'])
    def activity_log(self, request):
        """Get user login activities"""
        activities = LoginActivity.objects.filter(user=request.user)[:10]
        serializer = LoginActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def account_summary(self, request):
        """Get account activity summary"""
        user = request.user
        profile = user.profile
        
        # Get enrollment count
        enrollments_count = user.enrollments.filter(is_active=True).count() if hasattr(user, 'enrollments') else 0
        
        summary = {
            'total_study_days': profile.total_study_days,
            'total_notes': profile.total_notes,
            'active_courses': enrollments_count,
            'last_login': user.last_login_at,
            'account_created': user.created_at,
            'email_verified': user.email_verified,
        }
        
        return Response(summary)
class EmailTokenObtainPairView(TokenObtainPairView):
    """Custom JWT view using email-based authentication"""
    serializer_class = EmailTokenObtainPairSerializer