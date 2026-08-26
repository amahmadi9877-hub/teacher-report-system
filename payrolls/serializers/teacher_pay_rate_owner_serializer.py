from rest_framework.serializers import ValidationError

from core.serializers import SetOwnerJustTeacherSerializer
from payrolls.models import TeacherPayRate


class TeacherPayRateOwnerSerializer(SetOwnerJustTeacherSerializer):
    def validate(self, attrs):
        user = attrs.get("user_id")
        user_pay_rates = (
            TeacherPayRate.objects.filter(
                academic_term=self.instance.academic_term,
                owner_user=user,
            )
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if user_pay_rates:
            raise ValidationError(
                {
                    "owner_user": "Selected user is associated with another pay rate record!"
                }
            )
        return attrs
