# FILE: accounts/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('', include(router.urls)),
]