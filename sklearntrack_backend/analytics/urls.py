# FILE: analytics/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet, NotificationViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('dashboard/', AnalyticsViewSet.as_view({'get': 'dashboard'}), name='dashboard'),
    path('study-history/', AnalyticsViewSet.as_view({'get': 'study_history'}), name='study-history'),
] + router.urls

