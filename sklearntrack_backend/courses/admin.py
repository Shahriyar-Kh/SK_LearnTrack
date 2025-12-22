# FILE: courses/admin.py
# ============================================================================

from django.contrib import admin
from .models import (
    Course, Chapter, Topic, Subtopic, Exercise,
    Enrollment, SubtopicProgress, PersonalCourse
)


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1


class SubtopicInline(admin.TabularInline):
    model = Subtopic
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'estimated_duration', 'is_published', 'created_at']
    list_filter = ['difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'order']
    list_filter = ['chapter__course']
    inlines = [SubtopicInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'enrolled_at']
    list_filter = ['enrolled_at', 'course']
    search_fields = ['user__email', 'course__title']
