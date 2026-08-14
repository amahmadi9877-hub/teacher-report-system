from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from courses.models import CourseSchedule
from courses.serializers import (
    CourseSessionModelSerializer,
    CourseScheduleModelSerializer,
)
from courses.services import CourseSessionService


class CourseScheduleAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = CourseSchedule
    queryset = CourseSchedule.objects.all()
    serializer_class = CourseScheduleModelSerializer
    lookup_url_kwarg = "pk"

    @action(detail=True, methods=["POST"], url_path="create-sessions")
    def create_course_sessions(self, request, pk):
        course_schedule = self.get_object()

        sessions = CourseSessionService.create_from_schedule(
            course_schedule, request.user
        )
        serializer = CourseSessionModelSerializer(sessions, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
