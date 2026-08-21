from datetime import datetime

from django.utils import timezone

from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin, IsTeacher, IsOwner
from core.views import BaseModelViewSet
from core.serializers import SetOwnerJustTeacherSerializer
from courses.enums import CourseSessionStatus
from courses.models import CourseSession
from courses.serializers import CourseSessionModelSerializer
from reports.serializers import SessionReportSerializer
from reports.services import SessionReportService


class CourseSessionAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    PERMISSIONS_BY_ACTION = {
        "deactivate": [(IsEducationOfficer | (IsTeacher & IsOwner) | IsAdmin)],
        "retrieve": [(IsEducationOfficer | (IsTeacher & IsOwner) | IsAdmin)],
        "my_sessions": [(IsEducationOfficer | IsTeacher | IsAdmin)],
        "create_report": [(IsTeacher & IsOwner) | IsAdmin],
    }
    model = CourseSession
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionModelSerializer
    lookup_url_kwarg = "pk"
    set_owner_serializer_class = SetOwnerJustTeacherSerializer

    def perform_deactivate(self, serializer):
        obj = serializer.instance
        if (
            obj.status == CourseSessionStatus.COMPLETED
            and timezone.now() < datetime.combine(obj.date, obj.end_time)
        ):
            raise exceptions.PermissionDenied(
                detail="Completing the session before end_time is forbidden!"
            )
        if (
            obj.status == CourseSessionStatus.CANCELED
            and obj.sessionreport_set.exists()
        ):
            raise exceptions.PermissionDenied(
                detail="Canceling the session while it has report is forbidden!"
            )

        return super().perform_deactivate(serializer)

    def perform_set_owner(sefl, serializer):
        obj = serializer.instance
        if obj.sessionreport_set.exists():
            raise exceptions.PermissionDenied(
                detail="Changing the owner while it has report is forbidden!"
            )
        return super().perform_set_owner(serializer)

    @action(
        detail=False,
        methods=["GET"],
        url_path="my-sessions",
    )
    def my_sessions(self, request):
        sessions = CourseSession.objects.filter(owner_user=request.user)
        serializer = CourseSessionModelSerializer(sessions, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], url_path="create-report")
    def create_report(self, request, pk):
        course_session = self.get_object()

        report = SessionReportService.create_from_course_session(
            course_session, request.user
        )
        serializer = SessionReportSerializer(report)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
