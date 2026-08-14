from django.urls import path
from rest_framework.routers import DefaultRouter

from courses.views import (
    AcademicTermAPIModelViewSet,
    CourseAPIModelViewSet,
    CourseInstructorAPIModelViewSet,
    CourseScheduleAPIModelViewSet,
    CourseSessionAPIModelViewSet,
)

router = DefaultRouter(use_regex_path=False)
router.register(
    prefix="academic-term",
    viewset=AcademicTermAPIModelViewSet,
    basename="academic-term",
)
router.register(prefix="course", viewset=CourseAPIModelViewSet, basename="course")
router.register(
    prefix="course-instructor",
    viewset=CourseInstructorAPIModelViewSet,
    basename="course-instructor",
)
router.register(
    prefix="course-schedule",
    viewset=CourseScheduleAPIModelViewSet,
    basename="course-schedule",
)
router.register(
    prefix="course-session",
    viewset=CourseSessionAPIModelViewSet,
    basename="course-session",
)

urlpatterns = []

urlpatterns += router.urls
