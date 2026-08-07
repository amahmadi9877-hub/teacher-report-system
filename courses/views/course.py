from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEducationOfficerOrAdmin
from core.views import BaseModelViewSet
from courses.models import Course
from courses.serializers import CourseModelSerializer


class CourseAPIModelViewSet(BaseModelViewSet):
    permission_classes = [IsEducationOfficerOrAdmin, IsAuthenticated]
    model = Course
    queryset = Course.objects.all()
    serializer_class = CourseModelSerializer
    lookup_url_kwarg = "pk"
