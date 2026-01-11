# FILE: sklearntrack_backend/urls.py
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import EmailTokenObtainPairView  # Add this import
from django.http import JsonResponse  # Add this import

# Add a simple root view
def api_root(request):
    return JsonResponse({
    "message": "SK LearnTrack API is running!",
    "endpoints": {
        "admin": "/admin/",
        "token_obtain": "/api/token/",
        "token_refresh": "/api/token/refresh/",
        "auth": "/api/auth/",
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
    path('api/courses/', include('courses.urls')),
    path('api/', include('notes.urls')),
    path('api/roadmaps/', include('roadmaps.urls')),
    path('api/analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)