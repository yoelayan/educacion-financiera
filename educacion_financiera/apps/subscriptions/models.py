from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SubscriptionType(models.Model):
    """
    Subscription types available in the platform
    """
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(_("Duration (days)"), help_text=_("Duration in days, 0 for unlimited"))
    features = models.TextField(_("Features"), help_text=_("List of features, one per line"))
    is_active = models.BooleanField(_("Is active"), default=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        verbose_name = _("Subscription Type")
        verbose_name_plural = _("Subscription Types")
        ordering = ["price"]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    User subscription
    """
    STATUS_CHOICES = (
        ("active", _("Active")),
        ("cancelled", _("Cancelled")),
        ("expired", _("Expired")),
        ("pending", _("Pending")),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("User")
    )
    subscription_type = models.ForeignKey(
        SubscriptionType,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("Subscription Type")
    )
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="pending")
    start_date = models.DateTimeField(_("Start Date"), null=True, blank=True)
    end_date = models.DateTimeField(_("End Date"), null=True, blank=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    # Payment related fields
    payment_id = models.CharField(_("Payment ID"), max_length=100, blank=True)
    is_trial = models.BooleanField(_("Is Trial"), default=False)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-created"]
        get_latest_by = "created"

    def __str__(self):
        return f"{self.user.email} - {self.subscription_type.name} ({self.status})"
