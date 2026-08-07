from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEducationOfficerOrAdmin
from core.views import BaseModelViewSet
from courses.models import AcademicTerm
from courses.serializers import AcademicTermModelSerializer


class AcademicTermAPIModelViewSet(BaseModelViewSet):
    permission_classes = [IsEducationOfficerOrAdmin, IsAuthenticated]
    model = AcademicTerm
    queryset = AcademicTerm.objects.all()
    serializer_class = AcademicTermModelSerializer
    lookup_url_kwarg = "pk"
