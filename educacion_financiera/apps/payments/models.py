from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from educacion_financiera.apps.courses.models import Course
from educacion_financiera.apps.subscriptions.models import Subscription


class Payment(models.Model):
    """
    Payment model to track all payment transactions
    """
    PAYMENT_STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("completed", _("Completed")),
        ("failed", _("Failed")),
        ("refunded", _("Refunded")),
    )

    PAYMENT_TYPE_CHOICES = (
        ("subscription", _("Subscription")),
        ("course", _("Course")),
    )

    PROVIDER_CHOICES = (
        ("stripe", _("Stripe")),
        ("paypal", _("PayPal")),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("User")
    )
    payment_type = models.CharField(
        _("Payment Type"),
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default="USD")
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )
    provider = models.CharField(
        _("Provider"),
        max_length=20,
        choices=PROVIDER_CHOICES
    )
    provider_payment_id = models.CharField(_("Provider Payment ID"), max_length=255)
    provider_transaction_id = models.CharField(
        _("Provider Transaction ID"),
        max_length=255,
        blank=True
    )

    # References to related models (optional since can be subscription or course payment)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        related_name="payments",
        verbose_name=_("Subscription"),
        null=True,
        blank=True
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name="payments",
        verbose_name=_("Course"),
        null=True,
        blank=True
    )

    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    # Additional metadata
    metadata = models.JSONField(_("Metadata"), blank=True, null=True)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ["-created"]

    def __str__(self):
        return f"Payment {self.provider_payment_id} by {self.user.email} ({self.status})"

    def save(self, *args, **kwargs):
        # Ensure payment is for either a subscription or a course
        if self.payment_type == "subscription" and not self.subscription:
            raise ValueError("Subscription payment must have a subscription reference")
        if self.payment_type == "course" and not self.course:
            raise ValueError("Course payment must have a course reference")
        super().save(*args, **kwargs)
