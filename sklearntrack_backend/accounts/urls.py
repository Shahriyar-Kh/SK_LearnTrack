# FILE: accounts/urls.py - FIXED WITH ALL AUTH ROUTES
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('google_auth/', AuthViewSet.as_view({'post': 'google_auth'}), name='google_auth'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    
    # Password management
    path('request_password_reset/', AuthViewSet.as_view({'post': 'request_password_reset'}), name='request_password_reset'),
    path('reset_password/', AuthViewSet.as_view({'post': 'reset_password'}), name='reset_password'),
    
    # Email verification
    path('verify_email/', AuthViewSet.as_view({'post': 'verify_email'}), name='verify_email'),
    path('resend_verification/', AuthViewSet.as_view({'post': 'resend_verification'}), name='resend_verification'),
    
    # User management routes
    path('', include(router.urls)),
]