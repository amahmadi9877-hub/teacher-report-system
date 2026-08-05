from core.serializers import BaseModelSerializer
from organizations.models import School


class SchoolSerializer(BaseModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
