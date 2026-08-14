from rest_framework.serializers import ValidationError

from core.serializers import BaseModelSerializer
from core.validators import DateDifferenceValidator
from courses.models import CourseInstructor


class CourseInstructorModelSerializer(BaseModelSerializer):
    class Meta:
        model = CourseInstructor
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        course = attrs.get("course", getattr(self.instance, "course", None))
        if course is None:
            raise ValidationError({"course": "course is required!"})

        if start_date is None or end_date is None:
            raise ValidationError(
                {"__all__": "Both start date and end date are required!"}
            )

        DateDifferenceValidator(
            course.start_date,
            start_date,
            "course_start_date",
            "course_instructor_start_date",
        )
        DateDifferenceValidator(
            end_date,
            course.end_date,
            "course_instructor_end_date",
            "course_end_date",
        )

        DateDifferenceValidator(
            start_date,
            end_date,
            "course_instructor_start_date",
            "course_instructor_end_date",
        )

        course_instructors = course.courseinstructor_set.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if self.instance:
            course_instructors = course_instructors.exclude(pk=self.instance.pk)

        if course_instructors.exists():
            raise ValidationError(
                "The course instructore overlaps with an existing course instructore!"
            )

        return super().validate(attrs)
