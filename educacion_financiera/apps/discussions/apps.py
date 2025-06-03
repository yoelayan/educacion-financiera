from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiscussionsConfig(AppConfig):
    name = "educacion_financiera.apps.discussions"
    verbose_name = _("Discussions")

    def ready(self):
        try:
            import educacion_financiera.apps.discussions.signals  # noqa F401
        except ImportError:
            pass
