from rest_framework.serializers import ValidationError

from core.serializers import BaseModelSerializer
from core.validators import DateDifferenceValidator, TimeDifferenceValidator
from courses.models import CourseSession


class CourseSessionModelSerializer(BaseModelSerializer):
    class Meta:
        model = CourseSession
        fields = "__all__"

    def validate(self, attrs):
        course = attrs.get("course", getattr(self.instance, "course", None))
        if course is None:
            raise ValidationError({"course": "course is required!"})

        course_schedule = attrs.get(
            "course_schedule", getattr(self.instance, "course_schedule", None)
        )
        if course_schedule and course_schedule.course != course:
            raise ValidationError(
                {
                    "course_schedule": "The selected schedule does not belong to this course!"
                }
            )

        date = attrs.get("date", getattr(self.instance, "date", None))

        if date is None:
            raise ValidationError({"date": "Date is required!"})

        week_day = attrs.get("week_day", getattr(self.instance, "week_day", None))
        if week_day is None:
            raise ValidationError({"week_day": "Week day is required!"})

        DateDifferenceValidator(
            course.start_date,
            date,
            "course_start_date",
            "course_session_date",
        )
        DateDifferenceValidator(
            date,
            course.end_date,
            "course_session_date",
            "course_end_date",
        )

        if course_schedule:
            DateDifferenceValidator(
                course_schedule.start_date,
                date,
                "course_schedule_start_date",
                "course_session_date",
            )
            DateDifferenceValidator(
                date,
                course_schedule.end_date,
                "course_session_date",
                "course_schedule_end_date",
            )
        if date.weekday() != week_day:
            raise ValidationError({"__all__": "Date and week day do not match!"})

        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time is None or end_time is None:
            raise ValidationError(
                {"__all__": "Both start time and end time are required!"}
            )
        TimeDifferenceValidator(
            start_time,
            end_time,
            "course_session_start_time",
            "course_session_end_time",
            minimum_difference=course.session_duration,
            exact=True,
        )
        if course_schedule:
            TimeDifferenceValidator(
                course_schedule.start_time,
                start_time,
                "course_schedule_start_time",
                "course_session_start_time",
            )

            TimeDifferenceValidator(
                end_time,
                course_schedule.end_time,
                "course_session_end_time",
                "course_schedule_end_time",
            )

        if self.instance and self.instance.sessionreport_set.exists():
            if self.instance.date and self.instance.date != date:
                raise ValidationError(
                    {"date": "Course session has reports so can't change the date!"}
                )
            if self.instance.week_day and self.instance.week_day != week_day:
                raise ValidationError(
                    {
                        "week_day": "Course session has reports so can't change the week_day!"
                    }
                )
            if self.instance.start_time and self.instance.start_time != start_time:
                raise ValidationError(
                    {
                        "start_time": "Course session has reports so can't change the start_time!"
                    }
                )
            if self.instance.end_time and self.instance.end_time != end_time:
                raise ValidationError(
                    {
                        "end_time": "Course session has reports so can't change the end_times!"
                    }
                )
            if self.instance.course and self.instance.course != course:
                raise ValidationError(
                    {"course": "Course session has reports so can't change the course!"}
                )
            if (
                self.instance.course_schedule
                and self.instance.course_schedule != course_schedule
            ):
                raise ValidationError(
                    {
                        "course_schedule": "Course session has reports so can't change the course_schedule!"
                    }
                )

        return super().validate(attrs)
