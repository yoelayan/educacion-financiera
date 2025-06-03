from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Profile, Badge, UserBadge


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user", "role", "experience_level", "total_study_time_display",
        "current_streak", "courses_completed", "created"
    ]
    list_filter = [
        "role", "experience_level", "created", "email_notifications",
        "course_announcements", "public_profile"
    ]
    search_fields = ["user__email", "bio", "title", "company"]
    readonly_fields = ["created", "modified", "last_activity"]

    fieldsets = (
        (None, {
            "fields": ("user", "role", "photo", "bio")
        }),
        (_("Professional Information"), {
            "fields": ("title", "company", "experience_years"),
            "classes": ("collapse",)
        }),
        (_("Learning Preferences"), {
            "fields": ("experience_level", "interests"),
        }),
        (_("Social Media"), {
            "fields": ("website", "twitter", "facebook", "instagram", "linkedin", "youtube"),
            "classes": ("collapse",)
        }),
        (_("Privacy & Notifications"), {
            "fields": (
                "email_notifications", "course_announcements",
                "marketing_emails", "public_profile"
            ),
        }),
        (_("Learning Statistics"), {
            "fields": (
                "total_study_time", "courses_completed",
                "current_streak", "longest_streak", "last_activity"
            ),
            "classes": ("collapse",)
        }),
        (_("Metadata"), {
            "fields": ("created", "modified"),
            "classes": ("collapse",)
        }),
    )

    def total_study_time_display(self, obj):
        if obj.total_study_time:
            hours = obj.total_study_time // 60
            minutes = obj.total_study_time % 60
            return f"{hours}h {minutes}m"
        return "0m"
    total_study_time_display.short_description = _("Study Time")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "badge_type", "required_value", "color", "is_active", "earned_count"]
    list_filter = ["badge_type", "is_active", "color"]
    search_fields = ["name", "description"]
    ordering = ["badge_type", "required_value"]

    def earned_count(self, obj):
        return obj.earned_by.count()
    earned_count.short_description = _("Times Earned")

    fieldsets = (
        (None, {
            "fields": ("name", "description", "badge_type", "is_active")
        }),
        (_("Visual"), {
            "fields": ("icon", "color")
        }),
        (_("Criteria"), {
            "fields": ("required_value",)
        }),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ["user", "badge", "earned_at", "is_featured", "badge_type"]
    list_filter = ["earned_at", "is_featured", "badge__badge_type", "badge__is_active"]
    search_fields = ["user__email", "badge__name"]
    date_hierarchy = "earned_at"
    raw_id_fields = ["user", "badge"]
    readonly_fields = ["earned_at"]

    def badge_type(self, obj):
        return obj.badge.get_badge_type_display()
    badge_type.short_description = _("Badge Type")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'badge')
