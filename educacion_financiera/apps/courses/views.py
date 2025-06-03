from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Count, Avg, Prefetch

from .models import Category, Course, Enrollment, Lesson, Module, LessonProgress, Certificate


class CourseListView(ListView):
    """
    List all public courses
    """
    model = Course
    template_name = "apps/courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(visibility="public").select_related(
            "category", "instructor"
        ).annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count', '-created')

        # Filter by category
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Search functionality
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(overview__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["search_query"] = self.request.GET.get("q", "")

        # Add enrollment status for authenticated users
        if self.request.user.is_authenticated:
            enrolled_course_ids = list(Enrollment.objects.filter(
                student=self.request.user,
                active=True
            ).values_list('course_id', flat=True))
            context['enrolled_course_ids'] = enrolled_course_ids

        return context


class CategoryDetailView(DetailView):
    """
    Show details of a category and its courses
    """
    model = Category
    template_name = "apps/courses/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = self.object.courses.all()
        return context


class CourseDetailView(DetailView):
    """
    Show details of a course
    """
    model = Course
    template_name = "apps/courses/course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modules"] = self.object.modules.all().order_by("order").prefetch_related(
            'lessons__progress_records'
        )

        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(
                course=self.object,
                student=self.request.user,
                active=True
            ).exists()

            # Get user's progress for this course
            context["course_progress"] = self.object.get_progress_for_user(self.request.user)

            # Get module progress
            module_progress = {}
            for module in context["modules"]:
                module_progress[module.id] = module.get_progress_for_user(self.request.user)
            context["module_progress"] = module_progress

        return context


class ModuleDetailView(LoginRequiredMixin, DetailView):
    """
    Show details of a module
    """
    model = Module
    template_name = "apps/courses/module_detail.html"
    context_object_name = "module"

    def get_object(self):
        course_slug = self.kwargs["course_slug"]
        module_id = self.kwargs["module_id"]
        course = get_object_or_404(Course, slug=course_slug)

        # Check if user is enrolled
        if not Enrollment.objects.filter(
            course=course,
            student=self.request.user,
            active=True
        ).exists():
            # Redirect to course detail if not enrolled
            return redirect("courses:course_detail", slug=course_slug)

        return get_object_or_404(Module, id=module_id, course=course)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.object.course

        # Get lessons with progress information
        lessons = self.object.lessons.all().order_by("order")
        lesson_progress = {}
        for lesson in lessons:
            lesson_progress[lesson.id] = lesson.is_completed_by_user(self.request.user)

        context["lessons"] = lessons
        context["lesson_progress"] = lesson_progress
        context["module_progress"] = self.object.get_progress_for_user(self.request.user)

        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    """
    Show details of a lesson
    """
    model = Lesson
    template_name = "apps/courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_object(self):
        course_slug = self.kwargs["course_slug"]
        module_id = self.kwargs["module_id"]
        lesson_id = self.kwargs["pk"]

        course = get_object_or_404(Course, slug=course_slug)
        module = get_object_or_404(Module, id=module_id, course=course)

        # Check if user is enrolled
        if not Enrollment.objects.filter(
            course=course,
            student=self.request.user,
            active=True
        ).exists():
            # Redirect to course detail if not enrolled
            return redirect("courses:course_detail", slug=course_slug)

        return get_object_or_404(Lesson, id=lesson_id, module=module)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.object.module.course
        context["module"] = self.object.module

        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=self.request.user,
            lesson=self.object
        )
        context["lesson_progress"] = lesson_progress

        # Get user's notes
        if self.request.user.is_authenticated:
            from educacion_financiera.apps.discussions.models import Note
            try:
                context["note"] = Note.objects.get(lesson=self.object, user=self.request.user)
            except Note.DoesNotExist:
                context["note"] = None

        # Get comments
        from educacion_financiera.apps.discussions.models import Comment, Discussion
        context["comments"] = Comment.objects.filter(
            lesson=self.object,
            is_approved=True
        ).order_by("created")

        context["discussions"] = Discussion.objects.filter(
            lesson=self.object,
            is_active=True
        ).order_by("-created")

        # Get next and previous lessons
        context["next_lesson"] = self.object.get_next_lesson()
        context["previous_lesson"] = self.object.get_previous_lesson()

        return context

    def post(self, request, *args, **kwargs):
        """Handle lesson completion and note saving"""
        lesson = self.get_object()
        action = request.POST.get('action')

        if action == 'complete_lesson':
            # Mark lesson as completed
            lesson_progress, created = LessonProgress.objects.get_or_create(
                student=request.user,
                lesson=lesson
            )
            lesson_progress.mark_completed()

            # Update user profile activity
            profile = request.user.profile
            profile.update_activity_streak()

            # Check if course is completed and award certificate
            course = lesson.module.course
            if course.get_progress_for_user(request.user) == 100:
                certificate, created = Certificate.objects.get_or_create(
                    student=request.user,
                    course=course
                )
                if created:
                    messages.success(request, f'¡Felicidades! Has completado el curso "{course.title}" y obtenido tu certificado.')

            messages.success(request, f'Lección "{lesson.title}" marcada como completada.')

        elif action == 'save_note':
            # Save or update note
            from educacion_financiera.apps.discussions.models import Note
            note_content = request.POST.get('note_content', '').strip()

            if note_content:
                note, created = Note.objects.get_or_create(
                    lesson=lesson,
                    user=request.user,
                    defaults={'content': note_content}
                )
                if not created:
                    note.content = note_content
                    note.save()

                messages.success(request, 'Nota guardada exitosamente.')
            else:
                # Delete note if content is empty
                Note.objects.filter(lesson=lesson, user=request.user).delete()
                messages.info(request, 'Nota eliminada.')

        return redirect('courses:lesson_detail',
                       course_slug=lesson.module.course.slug,
                       module_id=lesson.module.id,
                       pk=lesson.id)


@method_decorator(csrf_exempt, name='dispatch')
class MarkLessonCompleteView(LoginRequiredMixin, View):
    """
    AJAX view to mark a lesson as completed
    """
    def post(self, request, *args, **kwargs):
        lesson_id = kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)

        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            course=lesson.module.course,
            student=request.user,
            active=True
        ).exists():
            return JsonResponse({'success': False, 'error': 'Not enrolled in course'})

        # Get or create progress record
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

        # Toggle completion status
        if progress.is_completed:
            progress.is_completed = False
            progress.completed_at = None
            action = 'uncompleted'
        else:
            progress.mark_completed()
            action = 'completed'

            # Update user profile activity
            profile, created = request.user.profile.get_or_create(user=request.user)
            profile.update_activity_streak()

        # Calculate new course progress
        course_progress = lesson.module.course.get_progress_for_user(request.user)

        # Check for course completion and certificate
        certificate_awarded = False
        if course_progress == 100 and action == 'completed':
            certificate, created = Certificate.objects.get_or_create(
                student=request.user,
                course=lesson.module.course
            )
            certificate_awarded = created

        return JsonResponse({
            'success': True,
            'action': action,
            'course_progress': course_progress,
            'certificate_awarded': certificate_awarded
        })


class CourseEnrollView(LoginRequiredMixin, View):
    """
    Enroll a student in a course
    """
    def post(self, request, *args, **kwargs):
        course_slug = self.kwargs["course_slug"]
        course = get_object_or_404(Course, slug=course_slug)

        # Check if course requires payment
        if course.price > 0:
            # Redirect to payment page
            return redirect("payments:course_checkout", course_slug=course_slug)

        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            course=course,
            student=request.user,
            defaults={"active": True}
        )

        if not created and not enrollment.active:
            enrollment.active = True
            enrollment.save()
            messages.success(request, f'Te has inscrito nuevamente en "{course.title}".')
        elif created:
            messages.success(request, f'Te has inscrito exitosamente en "{course.title}".')
        else:
            messages.info(request, f'Ya estás inscrito en "{course.title}".')

        # Redirect to course detail page
        return redirect("courses:course_detail", slug=course_slug)


class CourseUnenrollView(LoginRequiredMixin, View):
    """
    Unenroll a student from a course
    """
    def post(self, request, *args, **kwargs):
        course_slug = self.kwargs["course_slug"]
        course = get_object_or_404(Course, slug=course_slug)

        try:
            enrollment = Enrollment.objects.get(
                course=course,
                student=request.user,
                active=True
            )
            enrollment.active = False
            enrollment.save()
            messages.success(request, f'Te has desinscrito de "{course.title}".')
        except Enrollment.DoesNotExist:
            messages.error(request, 'No estás inscrito en este curso.')

        return redirect("courses:course_detail", slug=course_slug)


