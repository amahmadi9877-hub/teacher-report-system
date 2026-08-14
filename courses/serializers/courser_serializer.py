from rest_framework.serializers import ValidationError

from core.serializers import BaseModelSerializer
from core.validators import DateDifferenceValidator
from courses.models import Course


class CourseModelSerializer(BaseModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        academic_term = attrs.get(
            "academic_term", getattr(self.instance, "academic_term", None)
        )
        if academic_term is None:
            raise ValidationError({"academic_term": "academic_term is required!"})

        if start_date is None or end_date is None:
            raise ValidationError(
                {"__all__": "Both start date and end date are required!"}
            )

        DateDifferenceValidator(
            academic_term.start_date,
            start_date,
            "academic_term_start_date",
            "course_start_date",
        )
        DateDifferenceValidator(
            end_date,
            academic_term.end_date,
            "course_end_date",
            "academic_term_end_date",
        )

        DateDifferenceValidator(
            start_date,
            end_date,
            "course_start_date",
            "course_end_date",
        )

        if (
            self.instance
            and self.instance.courseinstructor_set.filter(
                start_date__lt=start_date
            ).exists()
        ):
            raise ValidationError(
                "There is at least one course instructor that starts before the selected start date!"
            )
        if (
            self.instance
            and self.instance.courseinstructor_set.filter(
                end_date__gt=end_date
            ).exists()
        ):
            raise ValidationError(
                "There is at least one course instructor that ends after the selected end date!"
            )

        if (
            self.instance
            and self.instance.courseschedule_set.filter(
                start_date__lt=start_date
            ).exists()
        ):
            raise ValidationError(
                "There is at least one course schedule that starts before the selected start date!"
            )
        if (
            self.instance
            and self.instance.courseschedule_set.filter(end_date__gt=end_date).exists()
        ):
            raise ValidationError(
                "There is at least one course schedule that ends after the selected end date!"
            )

        if (
            self.instance
            and self.instance.coursesession_set.filter(date__lt=start_date).exists()
        ):
            raise ValidationError(
                "There is at least one course session that starts before the selected start date!"
            )
        if (
            self.instance
            and self.instance.coursesession_set.filter(date__gt=end_date).exists()
        ):
            raise ValidationError(
                "There is at least one course session that ends after the selected end date!"
            )

        if (
            self.instance
            and self.instance.academic_term
            and self.instance.academic_term != academic_term
        ):
            if self.instance.courseinstructor_set.exists():
                raise ValidationError(
                    {
                        "academic_term": "Course has course_instructors so can't change the academic_term!"
                    }
                )
            if self.instance.courseschedule_set.exists():
                raise ValidationError(
                    {
                        "academic_term": "Course has course_schedules so can't change the academic_term!"
                    }
                )
            if self.instance.coursesession_set.exists():
                raise ValidationError(
                    {
                        "academic_term": "Course has course_sessions so can't change the academic_term!"
                    }
                )

        return super().validate(attrs)
