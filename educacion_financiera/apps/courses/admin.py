from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import (
    Category, Course, Enrollment, Lesson, Module, Resource,
    LessonProgress, Certificate
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "course_count"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = _("Courses")


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "instructor", "category", "price", "visibility", "enrollment_count", "created"]
    list_filter = ["visibility", "created", "category"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["instructor"]
    date_hierarchy = "created"
    inlines = [ModuleInline]

    def enrollment_count(self, obj):
        return obj.enrollments.filter(active=True).count()
    enrollment_count.short_description = _("Active Enrollments")


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    ordering = ['order']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "lesson_count"]
    list_filter = ["course"]
    search_fields = ["title", "description"]
    inlines = [LessonInline]

    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = _("Lessons")


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "module", "order", "completion_count"]
    list_filter = ["module__course", "module"]
    search_fields = ["title", "description"]
    inlines = [ResourceInline]

    def completion_count(self, obj):
        return obj.progress_records.filter(is_completed=True).count()
    completion_count.short_description = _("Completions")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "created"]
    list_filter = ["created"]
    search_fields = ["title"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "date_enrolled", "active", "progress_percentage"]
    list_filter = ["active", "date_enrolled", "course__category"]
    search_fields = ["student__email", "course__title"]
    date_hierarchy = "date_enrolled"
    raw_id_fields = ["student", "course"]

    def progress_percentage(self, obj):
        progress = obj.get_progress_percentage()
        color = "green" if progress >= 75 else "orange" if progress >= 50 else "red"
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            progress
        )
    progress_percentage.short_description = _("Progress")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "is_completed", "completed_at", "time_spent_display", "modified"]
    list_filter = ["is_completed", "completed_at", "lesson__module__course"]
    search_fields = ["student__email", "lesson__title"]
    date_hierarchy = "completed_at"
    raw_id_fields = ["student", "lesson"]
    readonly_fields = ["completed_at", "created", "modified"]

    def time_spent_display(self, obj):
        if obj.time_spent:
            minutes = obj.time_spent // 60
            seconds = obj.time_spent % 60
            return f"{minutes}m {seconds}s"
        return "0m"
    time_spent_display.short_description = _("Time Spent")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'lesson', 'lesson__module', 'lesson__module__course'
        )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "certificate_id", "issue_date", "is_active"]
    list_filter = ["issue_date", "is_active", "course__category"]
    search_fields = ["student__email", "course__title", "certificate_id"]
    date_hierarchy = "issue_date"
    raw_id_fields = ["student", "course"]
    readonly_fields = ["certificate_id", "issue_date"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'course', 'course__category'
        )
