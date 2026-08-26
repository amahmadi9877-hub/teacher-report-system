from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsFinanceOfficer, IsAdmin, IsTeacher
from core.views import BaseModelViewSet
from payrolls.models import Payroll
from payrolls.services import PayrollService
from payrolls.serializers import (
    PayrollSerializer,
    PayrollOwnerSerializer,
    YearAndMonthSerializer,
)


AUTH_USER = get_user_model()


class PayrollAPIModelViewSet(BaseModelViewSet):
    permission_classes = [(IsFinanceOfficer | IsAdmin)]
    PERMISSIONS_BY_ACTION = {
        "my_payrolls": [(IsFinanceOfficer | IsAdmin | IsTeacher)],
        "deactivate": [IsAdmin],
    }
    model = Payroll
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    assign_serializer_class = PayrollOwnerSerializer
    lookup_url_kwarg = "pk"

    @action(
        detail=True,
        methods=["POST"],
        url_path="calculate-price",
    )
    def calculate_price(self, request, pk):
        obj = self.get_object()
        payroll = PayrollService.calculate_price(obj)
        serializer = self.get_serializer(instance=payroll)

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["POST"],
        url_path="bulk-create",
    )
    def bulk_create(self, request):
        serializer = YearAndMonthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]
        teachers = AUTH_USER.objects.filter(role="teacher")
        data = PayrollService.bulk_create_and_calculate_price(
            request.user, teachers, year, month
        )
        return Response(data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="per-month",
    )
    def payrolls_per_month(self, request):
        serializer = YearAndMonthSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]
        payrolls = Payroll.objects.filter(year=year, month=month)
        serializer = self.get_serializer(payrolls, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="my-payrolls",
    )
    def my_payrolls(self, request):

        payrolls = Payroll.objects.filter(owner_user=request.user)
        serializer = self.get_serializer(payrolls, many=True)
        return Response(serializer.data)
