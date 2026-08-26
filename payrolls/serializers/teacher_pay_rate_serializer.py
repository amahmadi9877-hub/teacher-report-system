from core.serializers import BaseModelSerializer
from core.validators import posetive_decimal_validator
from payrolls.models import TeacherPayRate


class TeacherPayRateSerializer(BaseModelSerializer):
    class Meta:
        model = TeacherPayRate
        fields = "__all__"

    def validate(self, attrs):
        price_per_unit = attrs.get(
            "price_per_unit", getattr(self.instance, "price_per_unit", None)
        )
        posetive_decimal_validator(price_per_unit, "price_per_unit")

        return attrs
