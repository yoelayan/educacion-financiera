from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.CourseListView.as_view(), name="course_list"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("course/<slug:slug>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("course/<slug:course_slug>/module/<int:module_id>/",
         views.ModuleDetailView.as_view(),
         name="module_detail"),
    path("course/<slug:course_slug>/module/<int:module_id>/lesson/<int:pk>/",
         views.LessonDetailView.as_view(),
         name="lesson_detail"),
    path("course/<slug:course_slug>/enroll/",
         views.CourseEnrollView.as_view(),
         name="course_enroll"),
    path("course/<slug:course_slug>/unenroll/",
         views.CourseUnenrollView.as_view(),
         name="course_unenroll"),
    path("lesson/<int:lesson_id>/complete/", views.MarkLessonCompleteView.as_view(), name="mark_lesson_complete"),
]
