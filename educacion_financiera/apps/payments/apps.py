from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PaymentsConfig(AppConfig):
    name = "educacion_financiera.apps.payments"
    verbose_name = _("Payments")

    def ready(self):
        try:
            import educacion_financiera.apps.payments.signals  # noqa F401
        except ImportError:
            pass
