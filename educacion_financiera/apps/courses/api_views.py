from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone

from .models import (
    Category, Course, Module, Lesson, Enrollment,
    LessonProgress, Certificate
)
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    ModuleSerializer, LessonSerializer, EnrollmentSerializer,
    CertificateSerializer, LessonCompleteSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for course categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def courses(self, request, slug=None):
        """Get courses for a specific category"""
        category = self.get_object()
        courses = Course.objects.filter(
            category=category,
            visibility='public'
        ).select_related('category', 'instructor').annotate(
            enrollment_count=Count('enrollments')
        )

        serializer = CourseListSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for courses
    """
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Course.objects.filter(visibility='public').select_related(
            'category', 'instructor'
        ).annotate(
            enrollment_count=Count('enrollments')
        )

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(overview__icontains=search) |
                Q(category__name__icontains=search)
            )

        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)

        # Price filter
        price_filter = self.request.query_params.get('price', None)
        if price_filter == 'free':
            queryset = queryset.filter(price=0)
        elif price_filter == 'paid':
            queryset = queryset.filter(price__gt=0)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-enrollment_count')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll user in a course"""
        course = self.get_object()

        # Check if course requires payment
        if course.price > 0:
            return Response(
                {'error': 'Course requires payment', 'payment_required': True},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        # Get or create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            course=course,
            student=request.user,
            defaults={'active': True}
        )

        if not created and not enrollment.active:
            enrollment.active = True
            enrollment.save()

        serializer = EnrollmentSerializer(enrollment, context={'request': request})
        return Response({
            'enrolled': True,
            'enrollment': serializer.data,
            'message': 'Successfully enrolled in course'
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unenroll(self, request, slug=None):
        """Unenroll user from a course"""
        course = self.get_object()

        try:
            enrollment = Enrollment.objects.get(
                course=course,
                student=request.user,
                active=True
            )
            enrollment.active = False
            enrollment.save()

            return Response({
                'enrolled': False,
                'message': 'Successfully unenrolled from course'
            })
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Not enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def progress(self, request, slug=None):
        """Get user's progress in a course"""
        course = self.get_object()

        # Check if user is enrolled
        if not Enrollment.objects.filter(
            course=course, student=request.user, active=True
        ).exists():
            return Response(
                {'error': 'Not enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )

        progress_percentage = course.get_progress_for_user(request.user)
        total_lessons = course.get_total_lessons()
        completed_lessons = LessonProgress.objects.filter(
            lesson__module__course=course,
            student=request.user,
            is_completed=True
        ).count()

        return Response({
            'course_id': course.id,
            'progress_percentage': progress_percentage,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'lessons_remaining': total_lessons - completed_lessons
        })


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for lessons
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.select_related(
            'module', 'module__course'
        ).prefetch_related('resources')

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()

        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            course=lesson.module.course,
            student=request.user,
            active=True
        ).exists():
            return Response(
                {'error': 'Not enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark lesson as completed"""
        lesson = self.get_object()

        # Check enrollment
        if not Enrollment.objects.filter(
            course=lesson.module.course,
            student=request.user,
            active=True
        ).exists():
            return Response(
                {'error': 'Not enrolled in this course'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get or create progress
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

        # Update time spent if provided
        time_spent = request.data.get('time_spent', 0)
        if time_spent:
            progress.time_spent += time_spent

        # Mark as completed
        if not progress.is_completed:
            progress.mark_completed()

            # Update user profile activity
            if hasattr(request.user, 'profile'):
                request.user.profile.update_activity_streak()

        # Check for course completion
        course_progress = lesson.module.course.get_progress_for_user(request.user)
        certificate_awarded = False

        if course_progress == 100:
            certificate, created = Certificate.objects.get_or_create(
                student=request.user,
                course=lesson.module.course
            )
            certificate_awarded = created

        return Response({
            'completed': True,
            'course_progress': course_progress,
            'certificate_awarded': certificate_awarded,
            'message': 'Lesson marked as completed'
        })


class UserEnrollmentsAPIView(APIView):
    """
    Get user's enrolled courses
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            student=request.user,
            active=True
        ).select_related('course', 'course__category', 'course__instructor')

        serializer = EnrollmentSerializer(enrollments, many=True, context={'request': request})
        return Response(serializer.data)


class UserCertificatesAPIView(APIView):
    """
    Get user's certificates
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(
            student=request.user,
            is_active=True
        ).select_related('course', 'course__category')

        serializer = CertificateSerializer(certificates, many=True, context={'request': request})
        return Response(serializer.data)


class UserProgressAPIView(APIView):
    """
    Get user's overall learning progress
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get enrolled courses
        enrollments = Enrollment.objects.filter(
            student=request.user,
            active=True
        ).select_related('course')

        # Calculate statistics
        total_courses = enrollments.count()
        completed_courses = 0
        total_progress = 0
        total_lessons = 0
        completed_lessons = 0

        for enrollment in enrollments:
            course_progress = enrollment.course.get_progress_for_user(request.user)
            total_progress += course_progress

            if course_progress == 100:
                completed_courses += 1

            course_total_lessons = enrollment.course.get_total_lessons()
            total_lessons += course_total_lessons

            course_completed_lessons = LessonProgress.objects.filter(
                lesson__module__course=enrollment.course,
                student=request.user,
                is_completed=True
            ).count()
            completed_lessons += course_completed_lessons

        # Calculate averages
        avg_progress = round(total_progress / total_courses, 1) if total_courses > 0 else 0
        completion_rate = round((completed_courses / total_courses) * 100, 1) if total_courses > 0 else 0

        # Get certificates count
        certificates_count = Certificate.objects.filter(
            student=request.user,
            is_active=True
        ).count()

        # Get profile stats
        profile_stats = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile_stats = {
                'total_study_time': profile.total_study_time,
                'current_streak': profile.current_streak,
                'longest_streak': profile.longest_streak,
                'last_activity': profile.last_activity,
            }

        return Response({
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'avg_progress': avg_progress,
            'completion_rate': completion_rate,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'certificates_count': certificates_count,
            'profile_stats': profile_stats
        })


class LessonCompleteAPIView(APIView):
    """
    API endpoint to mark lessons as complete (alternative to viewset action)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LessonCompleteSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            lesson_id = serializer.validated_data['lesson_id']
            time_spent = serializer.validated_data.get('time_spent', 0)

            lesson = get_object_or_404(Lesson, id=lesson_id)

            # Get or create progress
            progress, created = LessonProgress.objects.get_or_create(
                student=request.user,
                lesson=lesson
            )

            # Update time spent
            if time_spent:
                progress.time_spent += time_spent

            # Mark as completed
            if not progress.is_completed:
                progress.mark_completed()

                # Update user profile
                if hasattr(request.user, 'profile'):
                    request.user.profile.update_activity_streak()

            # Check course completion
            course_progress = lesson.module.course.get_progress_for_user(request.user)
            certificate_awarded = False

            if course_progress == 100:
                certificate, created = Certificate.objects.get_or_create(
                    student=request.user,
                    course=lesson.module.course
                )
                certificate_awarded = created

            return Response({
                'success': True,
                'lesson_id': lesson_id,
                'completed': progress.is_completed,
                'course_progress': course_progress,
                'certificate_awarded': certificate_awarded
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
