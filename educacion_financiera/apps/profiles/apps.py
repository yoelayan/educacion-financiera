from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfilesConfig(AppConfig):
    name = "educacion_financiera.apps.profiles"
    verbose_name = _("Profiles")

    def ready(self):
        try:
            import educacion_financiera.apps.profiles.signals  # noqa F401
        except ImportError:
            pass
