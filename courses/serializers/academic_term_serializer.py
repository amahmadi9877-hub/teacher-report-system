from rest_framework.serializers import ValidationError

from core.serializers import BaseModelSerializer
from core.validators import DateDifferenceValidator
from courses.models import AcademicTerm


class AcademicTermModelSerializer(BaseModelSerializer):
    class Meta:
        model = AcademicTerm
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start_date is None or end_date is None:
            raise ValidationError(
                {"__all__": "Both start date and end date are required!"}
            )

        DateDifferenceValidator(
            start_date, end_date, "term_start_date", "term_end_date"
        )

        terms = AcademicTerm.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if self.instance:
            terms = terms.exclude(pk=self.instance.pk)

        if terms.exists():
            raise ValidationError("The academic term overlaps with an existing term!")

        if self.instance:
            if self.instance.course_set.filter(start_date__lt=start_date).exists():
                raise ValidationError(
                    "There is at least one course that starts before the selected start date!"
                )
            if self.instance.course_set.filter(end_date__gt=end_date).exists():
                raise ValidationError(
                    "There is at least one course that ends after the selected end date!"
                )
        return super().validate(attrs)
