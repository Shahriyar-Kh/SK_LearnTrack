# FILE: courses/urls.py
# ============================================================================
# URL routing for Course Management APIs
# ============================================================================
# Separates admin and student APIs for clear permission boundaries
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
try:
    from rest_framework_nested import routers
    HAS_NESTED_ROUTERS = True
except ImportError:
    HAS_NESTED_ROUTERS = False

from .views_admin import (
    AdminCourseViewSet, AdminChapterViewSet, AdminTopicViewSet,
    ReorderStructureViewSet
)
from .views_student import (
    StudentCourseViewSet, StudentTopicViewSet, QuizAttemptViewSet,
    StudentNoteViewSet, TopicBookmarkViewSet, StudentDashboardViewSet
)

# ============================================================================
# ADMIN ROUTERS
# ============================================================================

admin_router = DefaultRouter()
admin_router.register(r'courses', AdminCourseViewSet, basename='admin-course')

# Nested routers for chapters and topics (if available)
if HAS_NESTED_ROUTERS:
    courses_router = routers.NestedDefaultRouter(admin_router, r'courses', lookup='course')
    courses_router.register(r'chapters', AdminChapterViewSet, basename='admin-chapter')
    
    chapters_router = routers.NestedDefaultRouter(courses_router, r'chapters', lookup='chapter')
    chapters_router.register(r'topics', AdminTopicViewSet, basename='admin-topic')
else:
    courses_router = None
    chapters_router = None

# ============================================================================
# STUDENT ROUTERS
# ============================================================================

student_router = DefaultRouter()
student_router.register(r'courses', StudentCourseViewSet, basename='student-course')

# Nested routers for topics within courses
if HAS_NESTED_ROUTERS:
    courses_student_router = routers.NestedDefaultRouter(student_router, r'courses', lookup='course')
    courses_student_router.register(r'topics', StudentTopicViewSet, basename='student-topic')
    
    topics_student_router = routers.NestedDefaultRouter(
        courses_student_router, r'topics', lookup='topic'
    )
    topics_student_router.register(r'notes', StudentNoteViewSet, basename='student-note')
    topics_student_router.register(r'bookmarks', TopicBookmarkViewSet, basename='student-bookmark')
else:
    courses_student_router = None
    topics_student_router = None

# ============================================================================
# URL PATTERNS
# ============================================================================

urlpatterns = [
    # Admin APIs (protected)
    path('admin/', include(admin_router.urls)),
]

if HAS_NESTED_ROUTERS and courses_router:
    urlpatterns += [
        path('admin/', include(courses_router.urls)),
        path('admin/', include(chapters_router.urls)),
    ]

# Add fallback flat URLs for chapters and topics if no nested routers
if not HAS_NESTED_ROUTERS:
    urlpatterns += [
        path('admin/courses/<int:course_id>/chapters/', 
             AdminChapterViewSet.as_view({'post': 'create', 'get': 'list'}),
             name='admin-chapter-list'),
        path('admin/courses/<int:course_id>/chapters/<int:pk>/',
             AdminChapterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
             name='admin-chapter-detail'),
        path('admin/courses/<int:course_id>/chapters/<int:chapter_id>/topics/',
             AdminTopicViewSet.as_view({'post': 'create', 'get': 'list'}),
             name='admin-topic-list'),
        path('admin/courses/<int:course_id>/chapters/<int:chapter_id>/topics/<int:pk>/',
             AdminTopicViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
             name='admin-topic-detail'),
    ]

# Structure management
urlpatterns += [
    path(
        'admin/courses/<int:course_id>/structure/reorder/',
        ReorderStructureViewSet.as_view({'post': 'reorder'}),
        name='admin-reorder-structure'
    ),
]

# Student APIs (public for enrolled users)
urlpatterns += [path('', include(student_router.urls))]

if HAS_NESTED_ROUTERS and courses_student_router:
    urlpatterns += [
        path('', include(courses_student_router.urls)),
        path('', include(topics_student_router.urls)),
    ]

# Quiz submission
urlpatterns += [
    path(
        'courses/<int:course_id>/topics/<int:topic_id>/quiz-attempt/',
        QuizAttemptViewSet.as_view({'post': 'submit_quiz'}),
        name='student-quiz-attempt'
    ),
    
    # Dashboard
    path(
        'me/dashboard/',
        StudentDashboardViewSet.as_view({'get': 'dashboard'}),
        name='student-dashboard'
    ),
    path(
        'me/resume/',
        StudentDashboardViewSet.as_view({'get': 'resume'}),
        name='student-resume'
    ),
]
