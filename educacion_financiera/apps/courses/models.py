from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Categories for courses
    """
    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    description = models.TextField(_("Description"), blank=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("courses:category_detail", kwargs={"slug": self.slug})


class Course(models.Model):
    """
    Course model
    """
    VISIBILITY_CHOICES = (
        ("public", _("Public")),
        ("private", _("Private")),
        ("subscription", _("Subscription")),
    )

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        related_name="courses",
        on_delete=models.CASCADE,
        verbose_name=_("Category")
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="courses_created",
        on_delete=models.CASCADE,
        verbose_name=_("Instructor")
    )
    overview = models.TextField(_("Overview"))
    image = models.ImageField(
        _("Image"),
        upload_to="courses/%Y/%m/%d/",
        blank=True
    )
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("0 for free courses")
    )
    visibility = models.CharField(
        _("Visibility"),
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public"
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})

    def get_total_lessons(self):
        """Get total number of lessons in the course"""
        return Lesson.objects.filter(module__course=self).count()

    def get_progress_for_user(self, user):
        """Calculate progress percentage for a specific user"""
        if not user.is_authenticated:
            return 0

        total_lessons = self.get_total_lessons()
        if total_lessons == 0:
            return 0

        completed_lessons = LessonProgress.objects.filter(
            lesson__module__course=self,
            student=user,
            is_completed=True
        ).count()

        return round((completed_lessons / total_lessons) * 100, 1)


class Module(models.Model):
    """
    Module within a course
    """
    course = models.ForeignKey(
        Course,
        related_name="modules",
        on_delete=models.CASCADE,
        verbose_name=_("Course")
    )
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_progress_for_user(self, user):
        """Calculate progress percentage for a specific user in this module"""
        if not user.is_authenticated:
            return 0

        total_lessons = self.lessons.count()
        if total_lessons == 0:
            return 0

        completed_lessons = LessonProgress.objects.filter(
            lesson__module=self,
            student=user,
            is_completed=True
        ).count()

        return round((completed_lessons / total_lessons) * 100, 1)


class Lesson(models.Model):
    """
    Lesson within a module
    """
    module = models.ForeignKey(
        Module,
        related_name="lessons",
        on_delete=models.CASCADE,
        verbose_name=_("Module")
    )
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"))
    video_url = models.URLField(_("Video URL"), blank=True, help_text=_("YouTube or other video URL"))
    video_file = models.FileField(
        _("Video File"),
        upload_to="lessons/videos/%Y/%m/%d/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(_("Order"), default=0)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"

    def get_absolute_url(self):
        return reverse("courses:lesson_detail", kwargs={"pk": self.pk})

    def is_completed_by_user(self, user):
        """Check if lesson is completed by user"""
        if not user.is_authenticated:
            return False

        return LessonProgress.objects.filter(
            lesson=self,
            student=user,
            is_completed=True
        ).exists()

    def get_next_lesson(self):
        """Get the next lesson in order"""
        return Lesson.objects.filter(
            module=self.module,
            order__gt=self.order
        ).first()

    def get_previous_lesson(self):
        """Get the previous lesson in order"""
        return Lesson.objects.filter(
            module=self.module,
            order__lt=self.order
        ).last()


class Resource(models.Model):
    """
    Downloadable resources for lessons
    """
    lesson = models.ForeignKey(
        Lesson,
        related_name="resources",
        on_delete=models.CASCADE,
        verbose_name=_("Lesson")
    )
    title = models.CharField(_("Title"), max_length=200)
    file = models.FileField(_("File"), upload_to="lessons/resources/%Y/%m/%d/")
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """
    Course enrollment for students
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="enrollments",
        on_delete=models.CASCADE,
        verbose_name=_("Student")
    )
    course = models.ForeignKey(
        Course,
        related_name="enrollments",
        on_delete=models.CASCADE,
        verbose_name=_("Course")
    )
    date_enrolled = models.DateTimeField(_("Date Enrolled"), auto_now_add=True)
    active = models.BooleanField(_("Active"), default=True)

    class Meta:
        unique_together = [["student", "course"]]
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course.title}"

    def get_progress_percentage(self):
        """Get progress percentage for this enrollment"""
        return self.course.get_progress_for_user(self.student)


class LessonProgress(models.Model):
    """
    Track student progress through individual lessons
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lesson_progress",
        on_delete=models.CASCADE,
        verbose_name=_("Student")
    )
    lesson = models.ForeignKey(
        Lesson,
        related_name="progress_records",
        on_delete=models.CASCADE,
        verbose_name=_("Lesson")
    )
    is_completed = models.BooleanField(_("Is Completed"), default=False)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    time_spent = models.PositiveIntegerField(
        _("Time Spent (seconds)"),
        default=0,
        help_text=_("Time spent on this lesson in seconds")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        unique_together = [["student", "lesson"]]
        verbose_name = _("Lesson Progress")
        verbose_name_plural = _("Lesson Progress")
        ordering = ["-modified"]

    def __str__(self):
        return f"{self.student.email} - {self.lesson.title} ({'✓' if self.is_completed else '○'})"

    def mark_completed(self):
        """Mark lesson as completed"""
        if not self.is_completed:
            from django.utils import timezone
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()


class Certificate(models.Model):
    """
    Certificates awarded to students upon course completion
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="certificates",
        on_delete=models.CASCADE,
        verbose_name=_("Student")
    )
    course = models.ForeignKey(
        Course,
        related_name="certificates",
        on_delete=models.CASCADE,
        verbose_name=_("Course")
    )
    certificate_id = models.CharField(_("Certificate ID"), max_length=100, unique=True)
    issue_date = models.DateTimeField(_("Issue Date"), auto_now_add=True)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        unique_together = [["student", "course"]]
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Certificate for {self.student.email} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
