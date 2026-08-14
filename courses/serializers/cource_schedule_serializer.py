from rest_framework.serializers import ValidationError

from core.serializers import BaseModelSerializer
from core.validators import DateDifferenceValidator, TimeDifferenceValidator
from courses.models import CourseSchedule


class CourseScheduleModelSerializer(BaseModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = "__all__"

    def validate(self, attrs):
        course = attrs.get("course", getattr(self.instance, "course", None))
        if course is None:
            raise ValidationError({"course": "course is required!"})

        course_instructor = attrs.get(
            "course_instructor", getattr(self.instance, "course_instructor", None)
        )
        if course_instructor and course_instructor.course != course:
            raise ValidationError(
                {
                    "course_instructor": "The selected instructor does not belong to this course!"
                }
            )
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start_date is None or end_date is None:
            raise ValidationError(
                {"__all__": "Both start date and end date are required!"}
            )

        DateDifferenceValidator(
            start_date,
            end_date,
            "course_schedule_start_date",
            "course_schedule_end_date",
        )

        DateDifferenceValidator(
            course.start_date,
            start_date,
            "course_start_date",
            "course_schedule_start_date",
        )
        DateDifferenceValidator(
            end_date,
            course.end_date,
            "course_schedule_end_date",
            "course_end_date",
        )

        if course_instructor:
            DateDifferenceValidator(
                course_instructor.start_date,
                start_date,
                "course_instructor_start_date",
                "course_schedule_start_date",
            )
            DateDifferenceValidator(
                end_date,
                course_instructor.end_date,
                "course_schedule_end_date",
                "course_instructor_end_date",
            )
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time is None or end_time is None:
            raise ValidationError(
                {"__all__": "Both start time and end time are required!"}
            )
        TimeDifferenceValidator(
            start_time,
            end_time,
            "course_schedule_start_time",
            "course_schedule_end_time",
            minimum_difference=course.session_duration,
            exact=True,
        )

        return super().validate(attrs)
