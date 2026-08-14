from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin, IsTeacher, IsOwner
from core.views import BaseModelViewSet
from courses.models import CourseSession
from courses.serializers import CourseSessionModelSerializer


class CourseSessionAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    PERMISSIONS_BY_ACTION = {
        "deactivate": [(IsEducationOfficer | (IsTeacher & IsOwner) | IsAdmin)],
        "retrieve": [(IsEducationOfficer | (IsTeacher & IsOwner) | IsAdmin)],
        "my_sessions": [(IsEducationOfficer | IsTeacher | IsAdmin)],
    }
    model = CourseSession
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionModelSerializer
    lookup_url_kwarg = "pk"

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
