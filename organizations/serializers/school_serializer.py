from core.serializers import BaseModelSerializer
from organizations.models import School


class SchoolSerializer(BaseModelSerializer):
    class Meta:
        model = School
        fields = [
            "name",
            "manager",
            "business_phone",
            "address",
        ]
