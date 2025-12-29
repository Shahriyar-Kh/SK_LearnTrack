# FILE: accounts/views.py
# ============================================================================

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from .models import Profile, LoginActivity
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    ProfileSerializer, LoginActivitySerializer,
    EmailTokenObtainPairSerializer
)
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.GenericViewSet):
    """Authentication endpoints"""
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        logger.info(f"Registration attempt for email: {request.data.get('email', 'N/A')}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Track login activity
            self.track_login_activity(request, user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'redirect': '/dashboard'  # Always redirect students to dashboard
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.error(f"Registration validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user (blacklist refresh token)"""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out successfully")
            return Response(
                {'message': 'Logout successful'}, 
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            logger.error(f"Logout token error: {str(e)}")
            return Response(
                {'error': 'Invalid or expired token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'An error occurred during logout'}, 
                status=status.HTTP_400_BAD_REQUEST
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
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update user profile"""
        profile = request.user.profile
        serializer = ProfileSerializer(
            profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def activity_log(self, request):
        """Get user login activities"""
        activities = LoginActivity.objects.filter(user=request.user)[:10]
        serializer = LoginActivitySerializer(activities, many=True)
        return Response(serializer.data)


class EmailTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses email for authentication"""
    serializer_class = EmailTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Override to add login activity tracking"""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200 and 'user' in response.data:
            # Track login activity
            try:
                user_email = response.data['user']['email']
                user = User.objects.get(email=user_email)
                
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                LoginActivity.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                logger.error(f"Failed to track login activity: {str(e)}")
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip