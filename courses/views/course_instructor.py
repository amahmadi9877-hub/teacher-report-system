from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from courses.models import CourseInstructor
from courses.serializers import (
    CourseInstructorModelSerializer,
    CourseScheduleModelSerializer,
)
from courses.services import CourseScheduleService


class CourseInstructorAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = CourseInstructor
    queryset = CourseInstructor.objects.all()
    serializer_class = CourseInstructorModelSerializer
    lookup_url_kwarg = "pk"

    @action(detail=True, methods=["POST"], url_path="create-schedule")
    def create_course_schedule(self, request, pk):
        course_instructor = self.get_object()

        schedule = CourseScheduleService.create_from_instructor(
            course_instructor, request.user
        )
        serializer = CourseScheduleModelSerializer(schedule)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
