from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import Course, CourseInstructor, AcademicTerm, CourseSchedule
from organizations.models import School

AUTH_USER = get_user_model()


class CourseScheduleAPITest(APITestCase):
    def setUp(self):
        self.user = AUTH_USER.objects.create_superuser(
            username="admin", password="123", role="admin"
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.school = School.objects.create(
            name="school1", business_phone="02100000000"
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
            name="schedule 1",
            course=self.course,
            course_instructor=self.course_instructor,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 1),
            week_day=1,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        self.url = reverse("course-schedule-list")

    def test_create_valid_course_schedule(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_valid_course_schedule_without_instructor(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
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
            "name": "Schedule 2",
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_instructor_belonging_to_another_course(self):
        another_course = Course.objects.create(
            name="Course 2",
            academic_term=self.academic_term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )

        another_instructor = CourseInstructor.objects.create(
            course=another_course,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 15),
        )

        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": another_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "The selected instructor does not belong to this course!",
            str(response.data),
        )

    def test_create_without_start_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_end_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_after_end_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-20",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_before_course_start_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2025-12-15",
            "end_date": "2025-12-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_end_date_after_course_end_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-04-01",
            "end_date": "2026-04-01",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_before_instructor_start_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-01-10",
            "end_date": "2026-01-10",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_end_date_after_instructor_end_date(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-03-20",
            "end_date": "2026-03-20",
            "week_day": 1,
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
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "end_time": "10:30:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_end_time(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_invalid_session_duration(self):
        data = {
            "name": "Schedule 2",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-02-15",
            "week_day": 1,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_course_schedule_with_valid_data(self):
        url = reverse(
            "course-schedule-detail",
            kwargs={"pk": self.course_schedule.pk},
        )

        data = {
            "name": "Updated Schedule",
            "course": self.course.pk,
            "course_instructor": self.course_instructor.pk,
            "start_date": "2026-02-10",
            "end_date": "2026-02-10",
            "week_day": 2,
            "start_time": "14:00:00",
            "end_time": "15:30:00",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
