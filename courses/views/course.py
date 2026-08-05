from core.views import BaseModelViewSet
from courses.models import Course
from courses.serializers import CourseModelSerializer


class CourseAPIModelViewSet(BaseModelViewSet):
    model = Course
    queryset = Course.objects.all()
    serializer_class = CourseModelSerializer
    lookup_url_kwarg = "pk"
