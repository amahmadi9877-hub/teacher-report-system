from courses.views.academic_term import AcademicTermAPIModelViewSet
from courses.views.course_instructor import CourseInstructorAPIModelViewSet
from courses.views.course_schedule import CourseScheduleAPIModelViewSet
from courses.views.course_session import CourseSessionAPIModelViewSet
from courses.views.course import CourseAPIModelViewSet

__all__ = [
    "AcademicTermAPIModelViewSet",
    "CourseInstructorAPIModelViewSet",
    "CourseScheduleAPIModelViewSet",
    "CourseSessionAPIModelViewSet",
    "CourseAPIModelViewSet",
]
