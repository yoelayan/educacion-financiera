from django.urls import path

from .views import DashboardView, CourseSearchView, CertificatesView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("search/", CourseSearchView.as_view(), name="course_search"),
    path("certificates/", CertificatesView.as_view(), name="certificates"),
]
