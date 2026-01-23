import uuid

import pytest
from rest_framework import status

from courses.models import (
    Course,
    CourseChapter,
    CourseEnrollment,
    CourseStatus,
    CourseTopic,
)


def _build_course_payload():
    suffix = uuid.uuid4().hex[:6]
    return {
        "title": f"Backend Course {suffix}",
        "description": "End-to-end course for testing",
        "category": "python",
        "difficulty": "beginner",
        "estimated_hours": 4,
        "tags": ["backend", "django"],
        "meta_title": "Backend Course",
        "meta_description": "Backend course description",
    }


def _create_course_with_content(admin_client):
    payload = _build_course_payload()
    course_resp = admin_client.post("/api/courses/admin/courses/", payload, format="json")
    assert course_resp.status_code == status.HTTP_201_CREATED
    course = Course.objects.get(title=payload["title"])
    course_id = course.id

    chapter_resp = admin_client.post(
        f"/api/courses/admin/courses/{course_id}/chapters/",
        {
            "title": "Getting Started",
            "description": "Introduction chapter",
            "order_index": 0,
        },
        format="json",
    )
    if chapter_resp.status_code != status.HTTP_201_CREATED:
        print(f"Chapter creation failed: {chapter_resp.status_code}")
        print(f"Response data: {chapter_resp.data}")
    assert chapter_resp.status_code == status.HTTP_201_CREATED
    chapter = CourseChapter.objects.get(course=course, title="Getting Started")
    chapter_id = chapter.id

    topic_resp = admin_client.post(
        f"/api/courses/admin/courses/{course_id}/chapters/{chapter_id}/topics/",
        {
            "title": "Welcome",
            "description": "First topic",
            "content": "This is the first lesson content.",
            "estimated_minutes": 15,
            "difficulty": "beginner",
            "key_concepts": ["intro"],
            "order_index": 0,
        },
        format="json",
    )
    assert topic_resp.status_code == status.HTTP_201_CREATED
    topic = CourseTopic.objects.get(chapter=chapter, title="Welcome")
    topic_id = topic.id

    return {"course_id": course_id, "chapter_id": chapter_id, "topic_id": topic_id}


@pytest.mark.django_db
def test_admin_can_publish_course_with_content(admin_client):
    ids = _create_course_with_content(admin_client)

    publish_resp = admin_client.post(
        f"/api/courses/admin/courses/{ids['course_id']}/publish/",
        {"change_summary": "Ready for students"},
        format="json",
    )

    assert publish_resp.status_code == status.HTTP_200_OK
    assert publish_resp.data["status"] == CourseStatus.PUBLISHED
    assert Course.objects.get(id=ids["course_id"]).status == CourseStatus.PUBLISHED


@pytest.mark.django_db
def test_publish_requires_structure(admin_client):
    payload = _build_course_payload()
    course_resp = admin_client.post("/api/courses/admin/courses/", payload, format="json")
    assert course_resp.status_code == status.HTTP_201_CREATED
    course_id = Course.objects.get(title=payload["title"]).id

    publish_resp = admin_client.post(f"/api/courses/admin/courses/{course_id}/publish/", format="json")

    assert publish_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in publish_resp.data
    assert Course.objects.get(id=course_id).status == CourseStatus.DRAFT


@pytest.mark.django_db
def test_student_enrolls_and_reads_progress(admin_client, auth_client, user):
    ids = _create_course_with_content(admin_client)
    admin_client.post(
        f"/api/courses/admin/courses/{ids['course_id']}/publish/",
        {"change_summary": "Ready for enrollment"},
        format="json",
    )

    list_resp = auth_client.get("/api/courses/courses/")
    assert list_resp.status_code == status.HTTP_200_OK
    # Handle pagination if enabled
    if isinstance(list_resp.data, list):
        courses_data = list_resp.data
    elif isinstance(list_resp.data, dict):
        courses_data = list_resp.data.get('results', [])
    else:
        courses_data = []
    assert any(item["id"] == ids["course_id"] for item in courses_data)

    detail_resp = auth_client.get(f"/api/courses/courses/{ids['course_id']}/")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.data["id"] == ids["course_id"]

    enroll_resp = auth_client.post(f"/api/courses/courses/{ids['course_id']}/enroll/")
    assert enroll_resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
    assert CourseEnrollment.objects.filter(student=user, course_id=ids["course_id"]).exists()

    progress_resp = auth_client.get(f"/api/courses/courses/{ids['course_id']}/progress/")
    assert progress_resp.status_code == status.HTTP_200_OK
    assert progress_resp.data["total_topics"] == 1
    assert progress_resp.data["completed_topics"] == 0


@pytest.mark.django_db
def test_non_admin_cannot_create_course(auth_client):
    response = auth_client.post("/api/courses/admin/courses/", _build_course_payload(), format="json")
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
