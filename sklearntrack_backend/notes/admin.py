# FILE: notes/admin.py
# ============================================================================

from django.contrib import admin
from .models import (
    Note, NoteVersion, CodeSnippet, NoteSource,
    NoteTemplate, DailyNoteReport, AIGeneratedNote,
    YouTubeTranscript, NoteShare
)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'course', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'course']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    filter_horizontal = ['sources']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'slug', 'status')
        }),
        ('Content', {
            'fields': ('content', 'content_json', 'toc')
        }),
        ('Organization', {
            'fields': ('tags', 'course', 'topic', 'subtopic', 'session_date')
        }),
        ('References', {
            'fields': ('sources',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NoteVersion)
class NoteVersionAdmin(admin.ModelAdmin):
    list_display = ['note', 'version_number', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['note__title', 'changes_summary']
    readonly_fields = ['saved_at']


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'language', 'note', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['title', 'code', 'user__username']


@admin.register(NoteSource)
class NoteSourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'source_type', 'reference_number', 'created_at']
    list_filter = ['source_type', 'created_at']
    search_fields = ['title', 'url', 'author']
    readonly_fields = ['reference_number']


@admin.register(NoteTemplate)
class NoteTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_system', 'created_at']
    list_filter = ['is_system', 'created_at']
    search_fields = ['name', 'description']


@admin.register(DailyNoteReport)
class DailyNoteReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_date', 'notes_created', 'notes_updated', 'email_sent']
    list_filter = ['report_date', 'email_sent']
    search_fields = ['user__username']
    readonly_fields = ['created_at']


@admin.register(AIGeneratedNote)
class AIGeneratedNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'note', 'approved', 'created_at']
    list_filter = ['action_type', 'approved', 'created_at']
    search_fields = ['user__username', 'source_content']
    readonly_fields = ['created_at']


@admin.register(YouTubeTranscript)
class YouTubeTranscriptAdmin(admin.ModelAdmin):
    list_display = ['video_title', 'user', 'video_id', 'processed', 'created_at']
    list_filter = ['processed', 'created_at']
    search_fields = ['video_title', 'video_id', 'user__username']


@admin.register(NoteShare)
class NoteShareAdmin(admin.ModelAdmin):
    list_display = ['note', 'shared_by', 'shared_with', 'permission', 'is_public', 'created_at']
    list_filter = ['permission', 'is_public', 'created_at']
    search_fields = ['note__title', 'shared_by__username', 'shared_with__username']
    readonly_fields = ['public_slug', 'created_at']