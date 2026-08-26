from rest_framework import serializers
from core.enums import State
from core.serializers import BaseModelSerializer
from core.validators import posetive_int_validator
from courses.enums import CourseSessionStatus
from reports.models import SessionReport


class SessionReportSerializer(BaseModelSerializer):
    is_delayed = serializers.BooleanField(read_only=True)
    delay_minutes = serializers.IntegerField(read_only=True)
    reviewer_description = serializers.CharField(read_only=True)
    last_submit_date_time = serializers.DateTimeField(read_only=True)
    reference_date_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SessionReport
        fields = "__all__"

    def validate(self, attrs):
        course_session = attrs.get(
            "course_session", getattr(self.instance, "course_session", None)
        )
        if course_session is None:
            raise serializers.ValidationError(
                {"course_session": "course_session is required!"}
            )

        if (
            course_session.state != State.INACTIVE
            or course_session.status != CourseSessionStatus.COMPLETED
        ):
            raise serializers.ValidationError(
                {"course_session": "selected course_session is not completed!"}
            )

        if not course_session.owner_user:
            raise serializers.ValidationError(
                {"course_session": "selected course_session has not owner_user!"}
            )

        if (
            self.instance
            and self.instance.owner_user
            and course_session.owner_user != self.instance.owner_user
        ):
            raise serializers.ValidationError(
                {
                    "course_session": "The selected course session does not belong to the report owner!"
                }
            )
        request = self.context["request"]
        if (
            self.instance is None
            and request.user.role not in {"education", "admin"}
            and request.user != course_session.owner_user
        ):
            raise serializers.ValidationError(
                {
                    "course_session": "You do not have permission to create a report for the selected course session!"
                }
            )

        if (
            course_session
            and course_session != getattr(self.instance, "course_session", None)
            and course_session.sessionreport_set.exists()
        ):
            raise serializers.ValidationError(
                {
                    "course_session": (
                        "The selected course session already has a report!"
                    )
                }
            )

        posetive_int_validator(
            attrs.get("attendees", getattr(self.instance, "attendees", 0)), "attendees"
        )
        posetive_int_validator(
            attrs.get("absentees", getattr(self.instance, "absentees", 0)), "absentees"
        )

        return super().validate(attrs)
