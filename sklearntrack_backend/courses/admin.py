# FILE: courses/admin.py
# ============================================================================

from django.contrib import admin
from .models import (
    Course, CourseChapter, CourseTopic, CourseEnrollment, TopicProgress
)


class CourseChapterInline(admin.TabularInline):
    model = CourseChapter
    extra = 1


class CourseTopicInline(admin.TabularInline):
    model = CourseTopic
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'estimated_hours', 'status', 'created_at']
    list_filter = ['difficulty', 'status']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseChapterInline]


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order_index']
    list_filter = ['course']
    inlines = [CourseTopicInline]


@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'order_index']
    list_filter = ['chapter__course']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percentage', 'enrolled_at']
    list_filter = ['enrolled_at', 'course']
    search_fields = ['student__email', 'course__title']

