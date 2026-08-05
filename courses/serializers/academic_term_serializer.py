from core.serializers import BaseModelSerializer
from courses.models import AcademicTerm


class AcademicTermModelSerializer(BaseModelSerializer):
    class Meta:
        model = AcademicTerm
        fields = "__all__"
