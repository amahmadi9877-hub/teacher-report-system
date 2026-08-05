from core.serializers import BaseModelSerializer
from courses.models import Course


class CourseModelSerializer(BaseModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
