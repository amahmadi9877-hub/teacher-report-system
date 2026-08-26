from rest_framework.serializers import ValidationError

from core.serializers import SetOwnerJustTeacherSerializer
from payrolls.models import Payroll


class PayrollOwnerSerializer(SetOwnerJustTeacherSerializer):
    def validate(self, attrs):
        user = attrs.get("user_id")
        payrolls = (
            Payroll.objects.filter(
                year=self.instance.year,
                month=self.instance.month,
                owner_user=user,
            )
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if payrolls:
            raise ValidationError(
                {
                    "owner_user": "Selected user is associated with another pay rate record!"
                }
            )
        return attrs
