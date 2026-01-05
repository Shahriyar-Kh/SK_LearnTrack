# FILE: notes/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, ChapterViewSet, TopicViewSet, NoteShareViewSet
from .google_callback import GoogleOAuthCallbackView
from .views import execute_code

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'shares', NoteShareViewSet, basename='share')

urlpatterns = [
    # Put the callback URL BEFORE the router includes
    path('notes/google-callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('', include(router.urls)),
    path('notes/execute_code/', execute_code, name='execute_code'),
    
]