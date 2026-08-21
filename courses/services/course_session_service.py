from datetime import time, timedelta

from django.db import transaction
from django.utils import timezone

from courses.models import CourseSession


class CourseSessionService:
    @staticmethod
    @transaction.atomic
    def create_from_schedule(course_schedule, user):
        owner_user = None
        if course_schedule.course_instructor:
            owner_user = course_schedule.course_instructor.owner_user

        date_jump = (
            course_schedule.week_day - course_schedule.start_date.weekday()
            if course_schedule.week_day - course_schedule.start_date.weekday() >= 0
            else course_schedule.week_day - course_schedule.start_date.weekday() + 7
        )
        session_date = course_schedule.start_date + timedelta(days=date_jump)
        sessions_list = []
        while session_date <= course_schedule.end_date:
            sessions_list.append(
                CourseSession(
                    name=f"session {session_date}",
                    date=session_date,
                    week_day=course_schedule.week_day,
                    start_time=course_schedule.start_time,
                    end_time=course_schedule.end_time,
                    course=course_schedule.course,
                    course_schedule=course_schedule,
                    owner_user=owner_user,
                    responsible_user=owner_user,
                    created_by=user,
                    created_at=timezone.now(),
                    updated_by=user,
                    updated_at=timezone.now(),
                    state=1,
                    status=CourseSession.DEFAULT_ACTIVE_STATUS,
                )
            )
            session_date += timedelta(days=7)
        sessions = CourseSession.objects.bulk_create(sessions_list)
        return sessions
