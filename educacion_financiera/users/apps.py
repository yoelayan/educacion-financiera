import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "educacion_financiera.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import educacion_financiera.users.signals  # noqa: F401
