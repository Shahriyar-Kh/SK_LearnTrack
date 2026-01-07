# FILE: notes/urls.py - FIXED VERSION
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .google_callback import GoogleOAuthCallbackView
from . import views

router = DefaultRouter()
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'chapters', views.ChapterViewSet, basename='chapter')
router.register(r'topics', views.TopicViewSet, basename='topic')
router.register(r'shares', views.NoteShareViewSet, basename='share')
router.register(r'ai-history', views.AIHistoryViewSet, basename='ai-history')

urlpatterns = [
    # Callback URL - must be before router
    path('google-callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    
    # Code execution - must be before router
    path('run_code/', views.execute_code, name='run_code'),
    
    # Router includes all viewset URLs
    path('', include(router.urls)),
]