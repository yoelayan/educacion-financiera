from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoursesConfig(AppConfig):
    name = "educacion_financiera.apps.courses"
    verbose_name = _("Course Catalog")

    def ready(self):
        try:
            import educacion_financiera.apps.courses.signals  # noqa F401
        except ImportError:
            pass
