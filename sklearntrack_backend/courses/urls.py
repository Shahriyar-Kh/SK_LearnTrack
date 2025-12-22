# FILE: courses/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, EnrollmentViewSet,
    SubtopicViewSet, PersonalCourseViewSet
)

router = DefaultRouter()
router.register('', CourseViewSet, basename='course')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')
router.register('subtopics', SubtopicViewSet, basename='subtopic')
router.register('personal', PersonalCourseViewSet, basename='personal-course')

urlpatterns = router.urls
