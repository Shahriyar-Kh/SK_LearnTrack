# FILE: notes/admin.py
# ============================================================================

from django.contrib import admin
from .models import (
    Note,
    Chapter,
    ChapterTopic,
    TopicExplanation,
    TopicCodeSnippet,
    TopicSource,
    NoteVersion,
    AIGeneratedContent,
    NoteShare,
)

# ---------------------------------------------------------------------------
# NOTE
# ---------------------------------------------------------------------------

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'course', 'updated_at')
    list_filter = ('status', 'course', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}

# ---------------------------------------------------------------------------
# CHAPTER
# ---------------------------------------------------------------------------

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'note', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'note__title')
    ordering = ('note', 'order')

# ---------------------------------------------------------------------------
# TOPIC
# ---------------------------------------------------------------------------

@admin.register(ChapterTopic)
class ChapterTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'chapter', 'order', 'has_explanation', 'has_code', 'has_source')
    list_filter = ('created_at',)
    search_fields = ('name', 'chapter__title')
    ordering = ('chapter', 'order')

# ---------------------------------------------------------------------------
# TOPIC EXPLANATION
# ---------------------------------------------------------------------------

@admin.register(TopicExplanation)
class TopicExplanationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at')

# ---------------------------------------------------------------------------
# TOPIC CODE SNIPPET
# ---------------------------------------------------------------------------

@admin.register(TopicCodeSnippet)
class TopicCodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('language', 'created_at')
    list_filter = ('language',)
    search_fields = ('code',)
    readonly_fields = ('created_at', 'updated_at')

# ---------------------------------------------------------------------------
# TOPIC SOURCE
# ---------------------------------------------------------------------------

@admin.register(TopicSource)
class TopicSourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'created_at')
    search_fields = ('title', 'url')
    readonly_fields = ('created_at',)

# ---------------------------------------------------------------------------
# NOTE VERSIONING
# ---------------------------------------------------------------------------

@admin.register(NoteVersion)
class NoteVersionAdmin(admin.ModelAdmin):
    list_display = ('note', 'version_number', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('note__title',)
    readonly_fields = ('saved_at',)

# ---------------------------------------------------------------------------
# AI GENERATED CONTENT
# ---------------------------------------------------------------------------

@admin.register(AIGeneratedContent)
class AIGeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'topic', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__username', 'input_content')
    readonly_fields = ('created_at',)

# ---------------------------------------------------------------------------
# NOTE SHARING
# ---------------------------------------------------------------------------

@admin.register(NoteShare)
class NoteShareAdmin(admin.ModelAdmin):
    list_display = ('note', 'shared_by', 'shared_with', 'permission', 'is_public')
    list_filter = ('permission', 'is_public', 'created_at')
    search_fields = ('note__title', 'shared_by__username', 'shared_with__username')
    readonly_fields = ('public_slug', 'created_at')
