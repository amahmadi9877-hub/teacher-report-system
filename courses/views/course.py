from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from courses.models import Course
from courses.serializers import CourseModelSerializer, CourseScheduleModelSerializer
from courses.services import CourseScheduleService


class CourseAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = Course
    queryset = Course.objects.all()
    serializer_class = CourseModelSerializer
    lookup_url_kwarg = "pk"

    @action(detail=True, methods=["POST"], url_path="create-schedule")
    def create_course_schedule(self, request, pk):
        course = self.get_object()

        schedule = CourseScheduleService.create_from_course(course, request.user)
        serializer = CourseScheduleModelSerializer(schedule)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
