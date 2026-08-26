from rest_framework import exceptions


from core.permissions import IsFinanceOfficer, IsAdmin
from core.views import BaseModelViewSet
from payrolls.models import TeacherPayRate
from payrolls.serializers import TeacherPayRateSerializer, TeacherPayRateOwnerSerializer


class TeacherPayRateAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsFinanceOfficer | IsAdmin)]
    model = TeacherPayRate
    queryset = TeacherPayRate.objects.all()
    serializer_class = TeacherPayRateSerializer
    assign_serializer_class = TeacherPayRateOwnerSerializer
    lookup_url_kwarg = "pk"

    def perform_deactivate(self, serializer):
        if not serializer.instance.owner_user:
            raise exceptions.PermissionDenied({"owner_user": "owner user is required!"})
        return super().perform_deactivate(serializer)
