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


class CourseAPITest(APITestCase):
    def setUp(self):
        self.user = AUTH_USER.objects.create_superuser(
            username="admin", password="123", role="admin"
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.school = School.objects.create(
            name="School 1", business_phone="02100000000"
        )

        self.academic_term = AcademicTerm.objects.create(
            name="Term 1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            status=-1,
            state=-1,
        )

        self.course = Course.objects.create(
            name="Course 1",
            academic_term=self.academic_term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 5, 31),
        )

        self.url = reverse("course-list")

    def test_create_valid_course(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-15",
            "end_date": "2026-05-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_without_academic_term(self):
        data = {
            "name": "Course 2",
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-15",
            "end_date": "2026-05-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_start_date(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "end_date": "2026-05-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_end_date(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_before_academic_term_start_date(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2025-12-15",
            "end_date": "2026-05-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_after_academic_term_end_date(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-15",
            "end_date": "2026-07-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_after_end_date(self):
        data = {
            "name": "Course 2",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-05-15",
            "end_date": "2026-02-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_course_with_instructor_outside_new_date_range(self):
        CourseInstructor.objects.create(
            course=self.course,
            start_date=date(2026, 2, 15),
            end_date=date(2026, 5, 15),
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-03-01",
            "end_date": "2026-04-30",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course instructor that starts before the selected start date!",
            str(response.data),
        )

    def test_update_course_with_instructor_ending_after_new_end_date(self):
        CourseInstructor.objects.create(
            course=self.course,
            start_date=date(2026, 2, 15),
            end_date=date(2026, 5, 15),
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-01",
            "end_date": "2026-04-30",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course instructor that ends after the selected end date!",
            str(response.data),
        )

    def test_update_course_with_schedule_outside_new_start_date(self):
        CourseSchedule.objects.create(
            name="Schedule 1",
            course=self.course,
            start_date=date(2026, 2, 15),
            end_date=date(2026, 5, 15),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-03-01",
            "end_date": "2026-05-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course schedule that starts before the selected start date!",
            str(response.data),
        )

    def test_update_course_with_schedule_outside_new_end_date(self):
        CourseSchedule.objects.create(
            name="Schedule 1",
            course=self.course,
            start_date=date(2026, 2, 15),
            end_date=date(2026, 5, 15),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-01",
            "end_date": "2026-04-30",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course schedule that ends after the selected end date!",
            str(response.data),
        )

    def test_update_course_with_session_before_new_start_date(self):
        CourseSession.objects.create(
            name="Session 1",
            course=self.course,
            date=date(2026, 2, 15),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-03-01",
            "end_date": "2026-05-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course session that starts before the selected start date!",
            str(response.data),
        )

    def test_update_course_with_session_after_new_end_date(self):
        CourseSession.objects.create(
            name="Session 1",
            course=self.course,
            date=date(2026, 5, 15),
            week_day=4,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": self.academic_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-02-01",
            "end_date": "2026-04-30",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "There is at least one course session that ends after the selected end date!",
            str(response.data),
        )

    def test_change_academic_term_without_dependencies(self):
        another_term = AcademicTerm.objects.create(
            name="Term 2",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 12, 31),
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": another_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-08-01",
            "end_date": "2026-10-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


def test_cannot_change_academic_term_with_instructors(self):
    another_term = AcademicTerm.objects.create(
        name="Term 2",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 30),
    )

    CourseInstructor.objects.create(
        course=self.course,
        start_date=date(2026, 2, 15),
        end_date=date(2026, 5, 15),
    )

    url = reverse(
        "course-detail",
        kwargs={"pk": self.course.pk},
    )

    data = {
        "name": "Updated Course",
        "academic_term": another_term.pk,
        "school": self.school.pk,
        "session_duration": 90,
        "start_date": "2026-01-01",
        "end_date": "2026-06-30",
    }

    response = self.client.put(url, data)

    self.assertEqual(
        response.status_code,
        status.HTTP_400_BAD_REQUEST,
    )

    self.assertIn(
        "Course has course_instructors so can't change the academic_term!",
        str(response.data),
    )


def test_cannot_change_academic_term_with_schedules(self):
    another_term = AcademicTerm.objects.create(
        name="Term 2",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 30),
    )

    CourseSchedule.objects.create(
        name="Schedule 1",
        course=self.course,
        start_date=date(2026, 2, 15),
        end_date=date(2026, 5, 15),
        week_day=0,
        start_time="09:00:00",
        end_time="10:30:00",
    )

    url = reverse(
        "course-detail",
        kwargs={"pk": self.course.pk},
    )

    data = {
        "name": "Updated Course",
        "academic_term": another_term.pk,
        "school": self.school.pk,
        "session_duration": 90,
        "start_date": "2026-01-01",
        "end_date": "2026-06-30",
    }

    response = self.client.put(url, data)

    self.assertEqual(
        response.status_code,
        status.HTTP_400_BAD_REQUEST,
    )

    self.assertIn(
        "Course has course_schedules so can't change the academic_term!",
        str(response.data),
    )

    def test_cannot_change_academic_term_with_sessions(self):
        another_term = AcademicTerm.objects.create(
            name="Term 2",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
        )

        CourseSession.objects.create(
            name="Session 1",
            course=self.course,
            date=date(2026, 2, 2),
            week_day=0,
            start_time="09:00:00",
            end_time="10:30:00",
        )

        url = reverse(
            "course-detail",
            kwargs={"pk": self.course.pk},
        )

        data = {
            "name": "Updated Course",
            "academic_term": another_term.pk,
            "school": self.school.pk,
            "session_duration": 90,
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "Course has course_sessions so can't change the academic_term!",
            str(response.data),
        )
