from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsConfig(AppConfig):
    name = "educacion_financiera.apps.subscriptions"
    verbose_name = _("Subscriptions")

    def ready(self):
        try:
            import educacion_financiera.apps.subscriptions.signals  # noqa F401
        except ImportError:
            pass
