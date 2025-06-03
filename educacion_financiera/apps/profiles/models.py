from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    Extended profile for users
    """
    ROLE_CHOICES = (
        ("student", _("Student")),
        ("instructor", _("Instructor")),
    )

    EXPERIENCE_LEVEL_CHOICES = (
        ("beginner", _("Beginner")),
        ("intermediate", _("Intermediate")),
        ("advanced", _("Advanced")),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User")
    )
    role = models.CharField(
        _("Role"),
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )
    photo = models.ImageField(
        _("Photo"),
        upload_to="profiles/photos/%Y/%m/%d/",
        blank=True,
        null=True
    )
    bio = models.TextField(_("Biography"), blank=True)

    # Professional fields (mainly for instructors)
    title = models.CharField(_("Professional Title"), max_length=200, blank=True)
    company = models.CharField(_("Company"), max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(_("Years of Experience"), default=0)

    # Learning preferences (mainly for students)
    experience_level = models.CharField(
        _("Experience Level"),
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default="beginner"
    )

    # Interests (for both students and instructors)
    interests = models.TextField(
        _("Interests"),
        blank=True,
        help_text=_("Comma-separated list of financial topics of interest")
    )

    # Social media fields
    website = models.URLField(_("Website"), blank=True)
    twitter = models.CharField(_("Twitter"), max_length=100, blank=True)
    facebook = models.CharField(_("Facebook"), max_length=100, blank=True)
    instagram = models.CharField(_("Instagram"), max_length=100, blank=True)
    linkedin = models.CharField(_("LinkedIn"), max_length=100, blank=True)
    youtube = models.CharField(_("YouTube"), max_length=100, blank=True)

    # Privacy and notification preferences
    email_notifications = models.BooleanField(_("Email notifications"), default=True)
    course_announcements = models.BooleanField(_("Course announcements"), default=True)
    marketing_emails = models.BooleanField(_("Marketing emails"), default=False)
    public_profile = models.BooleanField(_("Public profile"), default=True)

    # Learning statistics
    total_study_time = models.PositiveIntegerField(
        _("Total Study Time (minutes)"),
        default=0,
        help_text=_("Total time spent studying in minutes")
    )
    courses_completed = models.PositiveIntegerField(_("Courses Completed"), default=0)
    current_streak = models.PositiveIntegerField(_("Current Streak (days)"), default=0)
    longest_streak = models.PositiveIntegerField(_("Longest Streak (days)"), default=0)
    last_activity = models.DateTimeField(_("Last Activity"), null=True, blank=True)

    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"Profile of {self.user.email}"

    @property
    def is_instructor(self):
        return self.role == "instructor"

    @property
    def is_student(self):
        return self.role == "student"

    @property
    def display_name(self):
        """Return user's display name"""
        if self.user.name:
            return self.user.name
        return self.user.email.split('@')[0]

    @property
    def completion_rate(self):
        """Calculate course completion rate"""
        from educacion_financiera.apps.courses.models import Enrollment
        enrollments = Enrollment.objects.filter(student=self.user, active=True)
        if not enrollments.exists():
            return 0

        total_courses = enrollments.count()
        completed_courses = sum(1 for e in enrollments if e.get_progress_percentage() == 100)
        return round((completed_courses / total_courses) * 100, 1)

    def get_interests_list(self):
        """Return interests as a list"""
        if not self.interests:
            return []
        return [interest.strip() for interest in self.interests.split(',') if interest.strip()]

    def update_study_time(self, minutes):
        """Add study time to total"""
        self.total_study_time += minutes
        self.save(update_fields=['total_study_time'])

    def update_activity_streak(self):
        """Update learning streak based on last activity"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        yesterday = now - timedelta(days=1)

        if not self.last_activity:
            self.current_streak = 1
        elif self.last_activity.date() == yesterday.date():
            self.current_streak += 1
        elif self.last_activity.date() != now.date():
            self.current_streak = 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_activity = now
        self.save(update_fields=['current_streak', 'longest_streak', 'last_activity'])


class Badge(models.Model):
    """
    Achievement badges for gamification
    """
    BADGE_TYPES = (
        ("completion", _("Course Completion")),
        ("streak", _("Learning Streak")),
        ("time", _("Study Time")),
        ("engagement", _("Community Engagement")),
        ("special", _("Special Achievement")),
    )

    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"))
    icon = models.CharField(_("Icon Class"), max_length=100, help_text=_("Font Awesome icon class"))
    badge_type = models.CharField(_("Badge Type"), max_length=20, choices=BADGE_TYPES)
    color = models.CharField(_("Color"), max_length=20, default="primary")

    # Criteria for earning the badge
    required_value = models.PositiveIntegerField(
        _("Required Value"),
        help_text=_("Minimum value required to earn this badge")
    )

    is_active = models.BooleanField(_("Is Active"), default=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")
        ordering = ["badge_type", "required_value"]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """
    Badges earned by users
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="earned_badges",
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    badge = models.ForeignKey(
        Badge,
        related_name="earned_by",
        on_delete=models.CASCADE,
        verbose_name=_("Badge")
    )
    earned_at = models.DateTimeField(_("Earned At"), auto_now_add=True)
    is_featured = models.BooleanField(_("Is Featured"), default=False)

    class Meta:
        unique_together = [["user", "badge"]]
        verbose_name = _("User Badge")
        verbose_name_plural = _("User Badges")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
