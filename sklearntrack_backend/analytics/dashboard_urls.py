# FILE: analytics/dashboard_urls.py
# ============================================================================
# Dedicated dashboard URL routes (separate from main analytics)

from django.urls import path
from .views import DashboardViewSet

urlpatterns = [
    path('overview/', DashboardViewSet.as_view({'get': 'overview'}), name='dashboard-overview'),
    path('recent-notes/', DashboardViewSet.as_view({'get': 'recent_notes'}), name='dashboard-recent-notes'),
    path('quick-actions/', DashboardViewSet.as_view({'get': 'quick_actions'}), name='dashboard-quick-actions'),
    path('today-plan/', DashboardViewSet.as_view({'get': 'today_plan', 'post': 'today_plan'}), name='dashboard-today-plan'),
    path('active-courses/', DashboardViewSet.as_view({'get': 'active_courses'}), name='dashboard-active-courses'),
]