from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Sum, Count
from django.views.generic import TemplateView, ListView
from django.utils import timezone
from datetime import timedelta

from educacion_financiera.apps.courses.models import Course, Enrollment, LessonProgress, Certificate
from educacion_financiera.apps.profiles.models import Profile


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for authenticated users showing their enrolled courses
    """
    template_name = "apps/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get or create user profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)

        # Get user's enrollments with related data
        enrollments = Enrollment.objects.filter(
            student=self.request.user,
            active=True
        ).select_related('course', 'course__category', 'course__instructor').prefetch_related(
            'course__modules__lessons'
        )

        # Get enrolled courses with progress
        enrolled_courses = []
        total_progress = 0
        total_study_time = 0

        for enrollment in enrollments:
            course = enrollment.course
            progress = course.get_progress_for_user(self.request.user)

            # Get current lesson/module info
            latest_progress = LessonProgress.objects.filter(
                student=self.request.user,
                lesson__module__course=course
            ).order_by('-modified').first()

            current_lesson = None
            current_module = None
            lessons_info = "Sin lecciones"

            if latest_progress:
                current_lesson = latest_progress.lesson
                current_module = current_lesson.module
                total_lessons = course.get_total_lessons()
                completed_lessons = LessonProgress.objects.filter(
                    student=self.request.user,
                    lesson__module__course=course,
                    is_completed=True
                ).count()
                lessons_info = f"Lección {completed_lessons + 1} de {total_lessons}"
            else:
                # Get first lesson
                first_module = course.modules.first()
                if first_module:
                    first_lesson = first_module.lessons.first()
                    if first_lesson:
                        current_lesson = first_lesson
                        current_module = first_module
                        total_lessons = course.get_total_lessons()
                        lessons_info = f"Lección 1 de {total_lessons}"

            enrolled_courses.append({
                'course': course,
                'progress': progress,
                'current_lesson': current_lesson,
                'current_module': current_module,
                'lessons_info': lessons_info,
                'enrollment': enrollment
            })

            total_progress += progress

        # Calculate average progress
        avg_progress = round(total_progress / len(enrolled_courses), 1) if enrolled_courses else 0

        # Get recommended courses (courses not enrolled in)
        enrolled_course_ids = [item['course'].id for item in enrolled_courses]
        recommended_courses = Course.objects.filter(
            visibility='public'
        ).exclude(
            id__in=enrolled_course_ids
        ).select_related('category', 'instructor').annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count', '-created')[:6]

        # Get certificates count
        certificates_count = Certificate.objects.filter(
            student=self.request.user,
            is_active=True
        ).count()

        # Calculate total study time from profile
        study_time_hours = profile.total_study_time // 60
        study_time_minutes = profile.total_study_time % 60
        if study_time_hours > 0:
            study_time_display = f"{study_time_hours}h {study_time_minutes}m"
        else:
            study_time_display = f"{study_time_minutes}m"

        # Get recent activity
        recent_progress = LessonProgress.objects.filter(
            student=self.request.user
        ).select_related('lesson', 'lesson__module', 'lesson__module__course').order_by('-modified')[:5]

        # Get user badges
        user_badges = self.request.user.earned_badges.select_related('badge')[:3]

        context.update({
            'enrolled_courses': enrolled_courses,
            'recommended_courses': recommended_courses,
            'total_courses': len(enrolled_courses),
            'avg_progress': avg_progress,
            'certificates': certificates_count,
            'study_time': study_time_display,
            'profile': profile,
            'recent_progress': recent_progress,
            'user_badges': user_badges,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'page_type': 'dashboard',
            'show_sidebar': True,
            'show_search': True,
        })

        return context


class CourseSearchView(LoginRequiredMixin, ListView):
    """
    Course search functionality
    """
    model = Course
    template_name = "apps/dashboard/course_search.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(visibility='public').select_related(
            'category', 'instructor'
        ).annotate(
            enrollment_count=Count('enrollments')
        )

        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        price_filter = self.request.GET.get('price')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query) |
                Q(category__name__icontains=query) |
                Q(instructor__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__slug=category)

        if price_filter == 'free':
            queryset = queryset.filter(price=0)
        elif price_filter == 'paid':
            queryset = queryset.filter(price__gt=0)

        # Default ordering
        sort = self.request.GET.get('sort', 'popularity')
        if sort == 'newest':
            queryset = queryset.order_by('-created')
        elif sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        else:  # popularity
            queryset = queryset.order_by('-enrollment_count', '-created')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get categories for filter
        from educacion_financiera.apps.courses.models import Category
        context['categories'] = Category.objects.all()

        # Get search parameters
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_level'] = self.request.GET.get('level', '')
        context['selected_price'] = self.request.GET.get('price', '')
        context['selected_sort'] = self.request.GET.get('sort', 'popularity')

        # Get user's enrolled courses for comparison
        if self.request.user.is_authenticated:
            enrolled_course_ids = list(Enrollment.objects.filter(
                student=self.request.user,
                active=True
            ).values_list('course_id', flat=True))
            context['enrolled_course_ids'] = enrolled_course_ids

        return context


class CertificatesView(LoginRequiredMixin, ListView):
    """
    User certificates view
    """
    model = Certificate
    template_name = "apps/dashboard/certificates.html"
    context_object_name = "certificates"
    paginate_by = 12

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('course', 'course__category', 'course__instructor').order_by('-issue_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get certificate statistics
        context['total_certificates'] = self.get_queryset().count()
        context['latest_certificate'] = self.get_queryset().first()

        # Get certificates by category
        certificates_by_category = {}
        for cert in self.get_queryset():
            category = cert.course.category.name
            if category not in certificates_by_category:
                certificates_by_category[category] = []
            certificates_by_category[category].append(cert)

        context['certificates_by_category'] = certificates_by_category

        return context
