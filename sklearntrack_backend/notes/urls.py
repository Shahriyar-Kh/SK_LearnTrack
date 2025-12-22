from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, CodeSnippetViewSet

router = DefaultRouter()
router.register('notes', NoteViewSet, basename='note')  # Changed from ''
router.register('snippets', CodeSnippetViewSet, basename='snippet')

urlpatterns = router.urls