from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, BooleanField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Educacion Financiera.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    # Role fields as specified in requirements
    is_student = BooleanField(_("Is Student"), default=True)
    is_teacher = BooleanField(_("Is Teacher"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    @property
    def user_type(self):
        """Get user type for display purposes"""
        if self.is_teacher:
            return "teacher"
        elif self.is_student:
            return "student"
        else:
            return "admin"

    def has_active_subscription(self):
        """Check if user has an active subscription"""
        from educacion_financiera.apps.subscriptions.models import Subscription
        return Subscription.objects.filter(
            user=self,
            status='active'
        ).exists()
