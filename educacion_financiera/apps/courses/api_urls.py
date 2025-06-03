from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    CategoryViewSet, CourseViewSet, LessonViewSet,
    UserEnrollmentsAPIView, UserCertificatesAPIView,
    UserProgressAPIView, LessonCompleteAPIView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')

app_name = 'courses_api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # User-specific endpoints
    path('user/enrollments/', UserEnrollmentsAPIView.as_view(), name='user-enrollments'),
    path('user/certificates/', UserCertificatesAPIView.as_view(), name='user-certificates'),
    path('user/progress/', UserProgressAPIView.as_view(), name='user-progress'),

    # Lesson completion endpoint
    path('lessons/complete/', LessonCompleteAPIView.as_view(), name='lesson-complete'),
]
