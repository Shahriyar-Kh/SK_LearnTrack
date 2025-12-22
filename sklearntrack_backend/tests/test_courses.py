import pytest
from courses.models import Course

@pytest.mark.django_db
def test_list_courses(auth_client):
    response = auth_client.get("/api/courses/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_detail(auth_client):
    course = Course.objects.create(
        title="Django",
        slug="django",
        description="Backend",
        difficulty="beginner",
        estimated_duration=10,
        is_published=True  # ← Important! Add this
    )
    response = auth_client.get(f"/api/courses/{course.slug}/")
    assert response.status_code == 200
