from django.urls import path
from rest_framework.routers import DefaultRouter

from courses.views import AcademicTermAPIModelViewSet, CourseAPIModelViewSet

router = DefaultRouter(use_regex_path=False)
router.register(
    prefix="academic-term",
    viewset=AcademicTermAPIModelViewSet,
    basename="academic-term",
)
router.register(prefix="course", viewset=CourseAPIModelViewSet, basename="course")

urlpatterns = []

urlpatterns += router.urls
