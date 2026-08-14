from datetime import time

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from courses.models import CourseSchedule


class CourseScheduleService:
    @staticmethod
    @transaction.atomic
    def create_from_instructor(course_instructor, user):
        start_time = time(8, 0)
        end_time = time(8, 0)
        if not course_instructor.owner_user:
            raise ValidationError(
                {"owner_user": "Owner user of course instructor is required!"}
            )
        return CourseSchedule.objects.create(
            name=f"schedule for {course_instructor.owner_user}",
            start_date=course_instructor.start_date,
            end_date=course_instructor.end_date,
            week_day=course_instructor.start_date.weekday(),
            start_time=start_time,
            end_time=end_time,
            session_count=0,
            course=course_instructor.course,
            course_instructor=course_instructor,
            created_by=user,
            created_at=timezone.now(),
            updated_by=user,
            updated_at=timezone.now(),
            state=1,
            status=CourseSchedule.DEFAULT_ACTIVE_STATUS,
        )

    @staticmethod
    @transaction.atomic
    def create_from_course(course, user):
        start_time = time(8, 0)
        end_time = time(8, 0)
        if not course.owner_user:
            raise ValidationError(
                {"owner_user": "Owner user of course instructor is required!"}
            )
        return CourseSchedule.objects.create(
            name=f"schedule from {course.name}",
            start_date=course.start_date,
            end_date=course.end_date,
            week_day=course.start_date.weekday(),
            start_time=start_time,
            end_time=end_time,
            session_count=0,
            course=course,
            created_by=user,
            created_at=timezone.now(),
            updated_by=user,
            updated_at=timezone.now(),
            state=1,
            status=CourseSchedule.DEFAULT_ACTIVE_STATUS,
        )
