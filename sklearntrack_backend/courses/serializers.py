# FILE: courses/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import (
    Course, Chapter, Topic, Subtopic, Exercise,
    Enrollment, SubtopicProgress, PersonalCourse,
    PersonalChapter, PersonalTopic
)


class SubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtopic
        fields = ['id', 'title', 'order', 'explanation', 'code_examples']


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'question', 'exercise_type', 'options', 'explanation']


class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubtopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'title', 'order', 'subtopics']


class ChapterSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'description', 'topics']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view"""
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'difficulty', 'estimated_duration', 'tags', 'is_published'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view"""
    
    chapters = ChapterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'difficulty', 'estimated_duration', 'tags',
            'is_published', 'chapters', 'created_at'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'progress_percentage',
            'last_accessed_subtopic', 'enrolled_at'
        ]


class SubtopicProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubtopicProgress
        fields = ['subtopic', 'completed', 'bookmarked', 'time_spent']


class PersonalCourseSerializer(serializers.ModelSerializer):
    """Serializer for personal courses"""
    
    class Meta:
        model = PersonalCourse
        fields = ['id', 'title', 'description', 'source', 'created_at']

