from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from organizations.models import School
from organizations.serializers import SchoolSerializer


class SchoolAPIModelViewSet(BaseModelViewSet):
    # permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = School
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    lookup_url_kwarg = "pk"
