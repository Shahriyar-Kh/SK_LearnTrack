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
from accounts.tasks import send_password_reset_email

from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uuid
import logging
from datetime import timedelta

from .models import Profile, LoginActivity, PasswordReset, EmailVerification
from .serializers import (
    UserRegistrationSerializer, UserSerializer, ProfileSerializer,
    LoginActivitySerializer, EmailTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    GoogleAuthSerializer, ProfileUpdateSerializer
)
from .permissions import IsAdminUser

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.GenericViewSet):
    """Enhanced authentication endpoints with proper error handling"""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user with proper validation and redirect"""
        logger.info(f"Registration attempt for email: {request.data.get('email', 'N/A')}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")
            
            # Send verification email (non-blocking)
            try:
                self.send_verification_email(user, request)
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                # Continue registration even if email fails
            
            # Generate tokens with custom claims
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['role'] = user.role
            refresh['full_name'] = user.full_name
            
            # Track login activity
            self.track_login_activity(request, user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': '/dashboard',
                'message': 'Registration successful! Please check your email to verify your account.',
                'success': True  # ✅ Added success flag for frontend
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Registration validation errors: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def google_auth(self, request):
        """Authenticate with Google OAuth"""
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Google auth serializer validation failed: {serializer.errors}")
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = serializer.validated_data['credential']
            google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            
            if not google_client_id or google_client_id == 'your-google-client-id.apps.googleusercontent.com':
                logger.error("Google OAuth Client ID is not configured in settings")
                return Response({
                    'error': 'Google OAuth is not configured on the server',
                    'detail': 'Please contact the administrator'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info("Verifying Google token...")
            
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            email = idinfo.get('email')
            google_id = idinfo.get('sub')
            full_name = idinfo.get('name', '')
            email_verified = idinfo.get('email_verified', False)
            
            if not email:
                return Response({
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = None
            created = False
            
            try:
                if google_id:
                    user = User.objects.get(google_id=google_id)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                    user.google_id = google_id
                    user.email_verified = email_verified
                    user.save()
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        email=email,
                        google_id=google_id,
                        full_name=full_name,
                        email_verified=email_verified,
                        terms_accepted=True,
                        role='student',
                    )
                    created = True
            
            if not user.is_active:
                return Response({
                    'error': 'User account is disabled'
                }, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['role'] = user.role
            refresh['full_name'] = user.full_name
            
            self.track_login_activity(request, user)
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            redirect_url = '/admin-dashboard' if user.role == 'admin' or user.is_staff else '/dashboard'
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': redirect_url,
                'is_new_user': created,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user and blacklist refresh token"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        """
        ✅ FIXED: Request password reset email
        - Always returns success to prevent email enumeration
        - Actually sends email if user exists
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email'].lower().strip()
        
        try:
            user = User.objects.get(email=email)
            
            # Create reset token
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=1)
            
            PasswordReset.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # ✅ FIXED: Send reset email with correct frontend URL
            try:
                self.send_password_reset_email(user, token, request)
                logger.info(f"Password reset email sent to: {email}")
            except Exception as e:
                logger.error(f"Failed to send reset email to {email}: {str(e)}")
                # Don't reveal the error to user
            
        except User.DoesNotExist:
            # ✅ SECURITY: Don't reveal that email doesn't exist
            logger.info(f"Password reset requested for non-existent email: {email}")
            pass
        
        # ✅ Always return success message (prevent email enumeration)
        return Response({
            'message': 'If an account exists with this email, you will receive a password reset link.',
            'success': True
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset password with token"""
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
                    'error': 'Invalid or expired reset token',
                    'success': False
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
                'message': 'Password reset successful. You can now login with your new password.',
                'success': True
            }, status=status.HTTP_200_OK)
            
        except PasswordReset.DoesNotExist:
            return Response({
                'error': 'Invalid reset token',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verify email with token"""
        token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification = EmailVerification.objects.get(token=token)
            
            if not verification.is_valid():
                return Response({
                    'error': 'Invalid or expired verification token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = verification.user
            user.email_verified = True
            user.save()
            
            verification.verified = True
            verification.save()
            
            return Response({
                'message': 'Email verified successfully!',
                'success': True
            }, status=status.HTTP_200_OK)
            
        except EmailVerification.DoesNotExist:
            return Response({
                'error': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        """Resend verification email"""
        email = request.data.get('email', '').lower().strip()
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                return Response({
                    'message': 'Email is already verified'
                }, status=status.HTTP_200_OK)
            
            self.send_verification_email(user, request)
            
            return Response({
                'message': 'Verification email sent',
                'success': True
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'message': 'If an account exists with this email, a verification link will be sent.',
                'success': True
            }, status=status.HTTP_200_OK)
    
    def send_verification_email(self, user, request):
        """Send email verification link"""
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)
        
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # ✅ Use FRONTEND_URL from settings
        frontend_url = settings.FRONTEND_URL
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        try:
            send_mail(
                subject='Verify your SK-LearnTrack account',
                message=f'Click here to verify your email: {verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Verification email sent to: {user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise
    
    def send_password_reset_email(self, user, token, request):
        frontend_url = settings.FRONTEND_URL
        reset_url = f"{frontend_url}/reset-password?token={token}"

        subject = 'Reset your SK-LearnTrack password'
        message = f'''Hello {user.full_name or user.email},

    You requested to reset your password.

    Click below (valid for 1 hour):
    {reset_url}

    If you did not request this, ignore this email.

    SK-LearnTrack Team
    '''

        # 🔥 IMPORTANT CHANGE (1 LINE)
        send_password_reset_email.delay(
            subject,
            message,
            user.email
        )

        
    def track_login_activity(self, request, user):
        """Track user login activity"""
        try:
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginActivity.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Failed to track login activity: {str(e)}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update user profile"""
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': 'Both old and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
    
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update user profile"""
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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