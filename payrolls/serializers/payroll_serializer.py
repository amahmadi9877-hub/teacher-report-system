from rest_framework.serializers import DecimalField


from core.serializers import BaseModelSerializer
from core.validators import posetive_decimal_validator
from payrolls.models import Payroll


class PayrollSerializer(BaseModelSerializer):
    total_price = DecimalField(max_digits=10, decimal_places=0, read_only=True)

    class Meta:
        model = Payroll
        fields = "__all__"
