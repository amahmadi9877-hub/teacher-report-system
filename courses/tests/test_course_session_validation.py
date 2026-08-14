from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import (
    Course,
    CourseInstructor,
    CourseSchedule,
    CourseSession,
    AcademicTerm,
)
from organizations.models import School

AUTH_USER = get_user_model()


class CourseSessionAPITest(APITestCase):
    def setUp(self):
        self.user = AUTH_USER.objects.create_superuser(
            username="admin", password="123", role="admin"
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.school = School.objects.create(
            name="school1",
            business_phone="02100000000",
        )
        self.academic_term = AcademicTerm.objects.create(
            name="term1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 4, 30),
            status=-1,
            state=-1,
        )
        self.course = Course.objects.create(
            name="course 1",
            academic_term=self.academic_term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )

        self.course_instructor = CourseInstructor.objects.create(
            name="instructore 1",
            course=self.course,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        self.course_schedule = CourseSchedule.objects.create(
            name="Schedule 1",
            course=self.course,
            course_instructor=self.course_instructor,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        self.course_session = CourseSession.objects.create(
            name="Session 1",
            course=self.course,
            course_schedule=self.course_schedule,
            date=date(2026, 2, 2),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        self.url = reverse("course-session-list")

    def test_create_valid_course_session(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_without_course(self):
        data = {
            "name": "Session 2",
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_schedule_belonging_to_another_course(self):
        another_course = Course.objects.create(
            name="Course 2",
            academic_term=self.academic_term,
            school=self.school,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            session_duration=90,
        )

        another_schedule = CourseSchedule.objects.create(
            name="Schedule 2",
            course=another_course,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": another_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "The selected schedule does not belong to this course!",
            str(response.data),
        )

    def test_create_without_date(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_week_day(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_date_and_week_day_mismatch(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-10",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "Date and week day do not match!",
            str(response.data),
        )

    def test_create_before_course_start_date(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2025-12-29",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_after_course_end_date(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-04-06",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_before_schedule_start_date(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-01-12",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_after_schedule_end_date(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-03-23",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_start_time(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_end_time(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_invalid_session_duration(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_time_before_schedule_start_time(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "08:00:00",
            "end_time": "09:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_end_time_after_schedule_end_time(self):
        data = {
            "name": "Session 2",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "10:00:00",
            "end_time": "11:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_valid_course_session(self):
        url = reverse(
            "course-session-detail",
            kwargs={"pk": self.course_session.pk},
        )

        data = {
            "name": "Updated Session",
            "course": self.course.pk,
            "course_schedule": self.course_schedule.pk,
            "date": "2026-02-09",
            "week_day": 0,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
