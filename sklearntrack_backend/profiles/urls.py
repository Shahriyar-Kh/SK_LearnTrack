# FILE: profiles/urls.py
# ============================================================================

from django.urls import path
from .views import ProfileViewSet

urlpatterns = [
    # Main profile endpoints
    path('', ProfileViewSet.as_view({
        'get': 'list',
        'patch': 'partial_update'
    }), name='profile'),
    
    # Avatar management
    path('avatar/', ProfileViewSet.as_view({
        'post': 'avatar'
    }), name='profile-avatar'),
    
    path('delete-avatar/', ProfileViewSet.as_view({
        'delete': 'delete_avatar'
    }), name='profile-delete-avatar'),
    
    # Preferences
    path('preferences/', ProfileViewSet.as_view({
        'get': 'preferences',
        'patch': 'preferences'
    }), name='profile-preferences'),
    
    # Notifications
    path('notifications/', ProfileViewSet.as_view({
        'get': 'notifications',
        'patch': 'notifications'
    }), name='profile-notifications'),
    
    # Security
    path('change-password/', ProfileViewSet.as_view({
        'post': 'change_password'
    }), name='profile-change-password'),
    
    # Activity
    path('activity/', ProfileViewSet.as_view({
        'get': 'activity'
    }), name='profile-activity'),
    
    path('activity-log/', ProfileViewSet.as_view({
        'get': 'activity_log'
    }), name='profile-activity-log'),
]