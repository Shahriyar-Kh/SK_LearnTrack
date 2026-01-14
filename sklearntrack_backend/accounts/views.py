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
    """Enhanced authentication endpoints with Google OAuth"""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        logger.info(f"Registration attempt for email: {request.data.get('email', 'N/A')}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")
            
            # Send verification email
            self.send_verification_email(user, request)
            
            # Generate tokens with custom claims
            refresh = RefreshToken.for_user(user)
            # Add custom claims to token
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
                'redirect': '/dashboard',  # Always redirect to user dashboard for students
                'message': 'Registration successful! Please check your email to verify your account.'
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Registration validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def google_auth(self, request):
        """
        Authenticate with Google OAuth - FIXED VERSION
        Accepts Google credential token and creates/logs in user
        """
        serializer = GoogleAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Google auth serializer validation failed: {serializer.errors}")
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify Google token
            token = serializer.validated_data['credential']
            
            # Get Google Client ID from settings
            google_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            
            if not google_client_id or google_client_id == 'your-google-client-id.apps.googleusercontent.com':
                logger.error("Google OAuth Client ID is not configured in settings")
                return Response({
                    'error': 'Google OAuth is not configured on the server',
                    'detail': 'Please contact the administrator'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info("Verifying Google token...")
            
            # Verify with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                google_client_id
            )
            
            logger.info(f"Google token verified. Issuer: {idinfo.get('iss')}")
            
            # Validate issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            # Extract user info
            email = idinfo.get('email')
            google_id = idinfo.get('sub')
            full_name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            email_verified = idinfo.get('email_verified', False)
            
            if not email:
                logger.error("Email not provided by Google")
                return Response({
                    'error': 'Email not provided by Google',
                    'detail': 'Please ensure email permission is granted'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Google OAuth user info: email={email}, google_id={google_id}")
            
            # Check if user exists
            user = None
            created = False
            
            try:
                # Try to find user by google_id first
                if google_id:
                    user = User.objects.get(google_id=google_id)
                    logger.info(f"Found existing user by google_id: {email}")
            except User.DoesNotExist:
                try:
                    # Try to find by email
                    user = User.objects.get(email=email)
                    # Link Google ID to existing account
                    user.google_id = google_id
                    user.email_verified = email_verified
                    user.save()
                    logger.info(f"Linked Google account to existing user: {email}")
                except User.DoesNotExist:
                    # Create new user
                    user = User.objects.create_user(
                        email=email,
                        google_id=google_id,
                        full_name=full_name,
                        email_verified=email_verified,
                        terms_accepted=True,
                        role='student',  # Default role for new users
                    )
                    created = True
                    logger.info(f"New user created via Google OAuth: {email}, role: {user.role}")
            
            # Ensure user is active
            if not user.is_active:
                logger.warning(f"Disabled user attempted Google login: {email}")
                return Response({
                    'error': 'User account is disabled',
                    'detail': 'Please contact support'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate tokens with custom claims
            refresh = RefreshToken.for_user(user)
            refresh['email'] = user.email
            refresh['role'] = user.role
            refresh['full_name'] = user.full_name
            refresh['is_staff'] = user.is_staff
            refresh['is_superuser'] = user.is_superuser
            
            # Track login activity
            self.track_login_activity(request, user)
            
            # Update last login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            # Determine redirect based on role 
            redirect_url = self.get_redirect_url(user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': redirect_url,
                'is_new_user': created,
            }
            
            logger.info(f"Google OAuth successful for: {user.email}, role: {user.role}, redirect: {redirect_url}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Google auth token verification error: {str(e)}")
            return Response({
                'error': 'Invalid Google token',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Google auth unexpected error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_redirect_url(self, user):
        """Determine redirect URL based on user role and profile completion"""
        # Admin users go to admin dashboard
        if user.role == 'admin' or user.is_staff or user.is_superuser:
            return '/admin-dashboard'
        # Regular users (including 'student' role) go to user dashboard
        return '/dashboard'
    
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
        """Request password reset email"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
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
            
            # Send reset email
            self.send_password_reset_email(user, token, request)
            
            return Response({
                'message': 'Password reset email sent. Please check your inbox.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'message': 'If an account exists with this email, you will receive a password reset link.'
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset password with token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset = PasswordReset.objects.get(token=token)
            
            if not reset.is_valid():
                return Response(
                    {'error': 'Invalid or expired reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update password
            user = reset.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset.used = True
            reset.save()
            
            return Response({
                'message': 'Password reset successful. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
            
        except PasswordReset.DoesNotExist:
            return Response(
                {'error': 'Invalid reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verify email with token"""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = EmailVerification.objects.get(token=token)
            
            if not verification.is_valid():
                return Response(
                    {'error': 'Invalid or expired verification token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify user email
            user = verification.user
            user.email_verified = True
            user.save()
            
            # Mark as verified
            verification.verified = True
            verification.save()
            
            return Response({
                'message': 'Email verified successfully!'
            }, status=status.HTTP_200_OK)
            
        except EmailVerification.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        """Resend verification email"""
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                return Response(
                    {'message': 'Email is already verified'},
                    status=status.HTTP_200_OK
                )
            
            self.send_verification_email(user, request)
            
            return Response({
                'message': 'Verification email sent'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'message': 'If an account exists with this email, a verification link will be sent.'},
                status=status.HTTP_200_OK
            )
    
    def send_verification_email(self, user, request):
        """Send email verification link"""
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)
        
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Build verification URL
        frontend_url = request.build_absolute_uri('/').rstrip('/')
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        # Send email
        try:
            send_mail(
                subject='Verify your SK-LearnTrack account',
                message=f'Click here to verify your email: {verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
    
    def send_password_reset_email(self, user, token, request):
        """Send password reset link"""
        frontend_url = request.build_absolute_uri('/').rstrip('/')
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        try:
            send_mail(
                subject='Reset your SK-LearnTrack password',
                message=f'Click here to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send reset email: {str(e)}")
    
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