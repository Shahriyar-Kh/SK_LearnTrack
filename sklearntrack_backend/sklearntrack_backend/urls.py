from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import EmailTokenObtainPairView
from analytics.views import DashboardViewSet  # ADD THIS IMPORT
from django.http import JsonResponse


def api_root(request):
    """API root endpoint with available routes"""
    return JsonResponse({
        "message": "SK LearnTrack API is running!",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "token_obtain": "/api/token/",
            "token_refresh": "/api/token/refresh/",
            "auth": "/api/auth/",
            "profile": "/api/profile/",
            "dashboard": "/api/dashboard/",  # ADD THIS
            "courses": "/api/courses/",
            "notes": "/api/",
            "roadmaps": "/api/roadmaps/",
            "analytics": "/api/analytics/",
        }
    })


urlpatterns = [
    # Root URL
    path('', api_root, name='api_root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # JWT Auth endpoints
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/auth/', include('accounts.urls')),
    path('api/profile/', include('profiles.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/', include('notes.urls')),
    path('api/roadmaps/', include('roadmaps.urls')),
    
    # Dashboard API - ADD THESE LINES
    path('api/dashboard/overview/', DashboardViewSet.as_view({'get': 'overview'}), name='dashboard-overview'),
    path('api/dashboard/recent-notes/', DashboardViewSet.as_view({'get': 'recent_notes'}), name='dashboard-recent-notes'),
    path('api/dashboard/quick-actions/', DashboardViewSet.as_view({'get': 'quick_actions'}), name='dashboard-quick-actions'),
    path('api/dashboard/today-plan/', DashboardViewSet.as_view({'get': 'today_plan', 'post': 'today_plan'}), name='dashboard-today-plan'),
    # END NEW LINES
    
    path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)