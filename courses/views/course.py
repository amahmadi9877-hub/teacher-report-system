from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from courses.models import Course
from courses.serializers import CourseModelSerializer


class CourseAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = Course
    queryset = Course.objects.all()
    serializer_class = CourseModelSerializer
    lookup_url_kwarg = "pk"
