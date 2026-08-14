from core.permissions import IsEducationOfficer, IsAdmin
from core.views import BaseModelViewSet
from courses.models import AcademicTerm
from courses.serializers import AcademicTermModelSerializer


class AcademicTermAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsEducationOfficer | IsAdmin)]
    model = AcademicTerm
    queryset = AcademicTerm.objects.all()
    serializer_class = AcademicTermModelSerializer
    lookup_url_kwarg = "pk"
