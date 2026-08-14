from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from organizations.models import School
from organizations.serializers import SchoolSerializer
from courses.serializers import CourseModelSerializer


class SchoolAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = School
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_url_kwarg = "pk"

    @action(
        detail=True,
        methods=["GET"],
        url_path="courses",
    )
    def courses(self, request, pk):
        school = self.get_object()
        courses = school.course_set.all()
        serializer = CourseModelSerializer(courses, many=True)
        return Response(serializer.data)
