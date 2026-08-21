from datetime import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from courses.enums import CourseSessionStatus
from reports.models import SessionReport


class SessionReportService:
    @staticmethod
    @transaction.atomic
    def create_from_course_session(course_session, user):

        if not course_session.owner_user:
            raise ValidationError({"owner_user": "Owner_user is required!"})

        print(course_session.owner_user, user)

        if course_session.owner_user != user:
            raise ValidationError(
                {
                    "__all__": "This is not your session! you are not allowed to create report for this session!"
                }
            )

        if course_session.status != CourseSessionStatus.COMPLETED:
            raise ValidationError({"status": "Course_session is not completed!"})

        if course_session.sessionreport_set.exists():
            raise ValidationError(
                {"course_session": "The course session already has a report!"}
            )

        return SessionReport.objects.create(
            name=f"report for {course_session.name}",
            course_session=course_session,
            reference_date_time=datetime.combine(
                course_session.date, course_session.end_time
            ),
            report_description="session summery",
            attendees=0,
            absentees=0,
            created_by=user,
            created_at=timezone.now(),
            updated_by=user,
            updated_at=timezone.now(),
            state=1,
            status=SessionReport.DEFAULT_ACTIVE_STATUS,
            owner_user=user,
            responsible_user=user,
        )
