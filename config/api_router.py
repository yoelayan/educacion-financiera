from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from educacion_financiera.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = [
    # Main router URLs
    path("", include(router.urls)),

    # Courses API
    path("courses/", include("educacion_financiera.apps.courses.api_urls")),
]
