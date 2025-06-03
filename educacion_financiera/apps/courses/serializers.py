from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Category, Course, Module, Lesson, Resource,
    Enrollment, LessonProgress, Certificate
)
from educacion_financiera.apps.profiles.models import Profile

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'course_count', 'created']

    def get_course_count(self, obj):
        return obj.courses.filter(visibility='public').count()


class InstructorSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'display_name', 'profile']

    def get_display_name(self, obj):
        return obj.name if obj.name else obj.email.split('@')[0]

    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'photo': profile.photo.url if profile.photo else None,
                'bio': profile.bio,
                'title': profile.title,
                'company': profile.company,
                'experience_years': profile.experience_years,
            }
        except Profile.DoesNotExist:
            return None


class ResourceSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ['id', 'title', 'file_url', 'created']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['id', 'is_completed', 'completed_at', 'time_spent', 'created', 'modified']


class LessonSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    video_url_embed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'video_url', 'video_url_embed',
            'order', 'resources', 'progress', 'created'
        ]

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = LessonProgress.objects.get(lesson=obj, student=request.user)
                return LessonProgressSerializer(progress).data
            except LessonProgress.DoesNotExist:
                return None
        return None

    def get_video_url_embed(self, obj):
        """Convert YouTube URL to embed format"""
        if obj.video_url and 'youtube.com/watch?v=' in obj.video_url:
            video_id = obj.video_url.split('watch?v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return obj.video_url


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'lessons',
            'progress', 'lessons_count', 'created'
        ]

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_progress_for_user(request.user)
        return 0

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for course listings"""
    category = CategorySerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'category', 'instructor', 'overview',
            'image_url', 'price', 'visibility', 'enrollment_count',
            'progress', 'is_enrolled', 'total_lessons', 'created'
        ]

    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(active=True).count()

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_progress_for_user(request.user)
        return 0

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                course=obj, student=request.user, active=True
            ).exists()
        return False

    def get_total_lessons(self, obj):
        return obj.get_total_lessons()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class CourseDetailSerializer(CourseListSerializer):
    """Detailed serializer for individual course views"""
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['modules']


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'date_enrolled', 'active', 'progress_percentage']

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()


class CertificateSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'course', 'certificate_id', 'issue_date', 'is_active']


class LessonCompleteSerializer(serializers.Serializer):
    """Serializer for marking lessons as complete"""
    lesson_id = serializers.IntegerField()
    time_spent = serializers.IntegerField(default=0)

    def validate_lesson_id(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        try:
            lesson = Lesson.objects.get(id=value)
            # Check if user is enrolled in the course
            if not Enrollment.objects.filter(
                course=lesson.module.course,
                student=request.user,
                active=True
            ).exists():
                raise serializers.ValidationError("Not enrolled in this course")
            return value
        except Lesson.DoesNotExist:
            raise serializers.ValidationError("Lesson not found")
