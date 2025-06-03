from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment, Discussion, Note


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ["created", "modified"]
    fields = ["body", "created_by", "is_approved", "created", "modified"]


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "created_by", "created", "is_active"]
    list_filter = ["is_active", "created", "lesson__module__course"]
    search_fields = ["title", "body", "created_by__email"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
    raw_id_fields = ["lesson", "created_by"]
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["get_comment_source", "created_by", "created", "is_approved"]
    list_filter = ["is_approved", "created"]
    search_fields = ["body", "created_by__email"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
    raw_id_fields = ["discussion", "lesson", "parent", "created_by"]

    def get_comment_source(self, obj):
        if obj.discussion:
            return f"Discussion: {obj.discussion.title}"
        elif obj.lesson:
            return f"Lesson: {obj.lesson.title}"
        elif obj.parent:
            return f"Reply to: {obj.parent}"
        return "Unknown"
    get_comment_source.short_description = _("Source")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["user", "lesson", "created", "modified"]
    list_filter = ["created", "lesson__module__course"]
    search_fields = ["content", "user__email", "lesson__title"]
    date_hierarchy = "created"
    readonly_fields = ["created", "modified"]
    raw_id_fields = ["lesson", "user"]
