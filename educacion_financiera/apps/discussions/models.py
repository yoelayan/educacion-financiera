from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from educacion_financiera.apps.courses.models import Lesson


class Discussion(models.Model):
    """
    Discussion thread for a lesson
    """
    lesson = models.ForeignKey(
        Lesson,
        related_name="discussions",
        on_delete=models.CASCADE,
        verbose_name=_("Lesson")
    )
    title = models.CharField(_("Title"), max_length=255)
    body = models.TextField(_("Body"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="discussions_created",
        on_delete=models.CASCADE,
        verbose_name=_("Created by")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Discussion")
        verbose_name_plural = _("Discussions")
        ordering = ["-created"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment on a discussion thread or lesson
    """
    # Comment can be on a discussion or directly on a lesson
    discussion = models.ForeignKey(
        Discussion,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("Discussion"),
        null=True,
        blank=True
    )
    lesson = models.ForeignKey(
        Lesson,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("Lesson"),
        null=True,
        blank=True
    )
    # Comment can be a reply to another comment
    parent = models.ForeignKey(
        'self',
        related_name="replies",
        on_delete=models.CASCADE,
        verbose_name=_("Parent comment"),
        null=True,
        blank=True
    )
    body = models.TextField(_("Body"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("Created by")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)
    is_approved = models.BooleanField(_("Is approved"), default=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["created"]

    def __str__(self):
        return f"Comment by {self.created_by.email} on {self.created}"

    def save(self, *args, **kwargs):
        # Ensure comment is either on a discussion or on a lesson, but not both
        if self.discussion and self.lesson:
            raise ValueError("Comment can't be on both a discussion and a lesson")
        if not self.discussion and not self.lesson:
            raise ValueError("Comment must be on either a discussion or a lesson")
        super().save(*args, **kwargs)


class Note(models.Model):
    """
    Personal note for a student on a specific lesson
    """
    lesson = models.ForeignKey(
        Lesson,
        related_name="notes",
        on_delete=models.CASCADE,
        verbose_name=_("Lesson")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    content = models.TextField(_("Content"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        ordering = ["-modified"]
        unique_together = [["lesson", "user"]]

    def __str__(self):
        return f"Note by {self.user.email} for {self.lesson}"
