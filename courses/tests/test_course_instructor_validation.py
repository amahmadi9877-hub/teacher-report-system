from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import Course, CourseInstructor, AcademicTerm
from organizations.models import School

AUTH_USER = get_user_model()


class CourseInstructorAPITest(APITestCase):
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

        self.url = reverse("course-instructor-list")

    def test_create_valid_course_instructor(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-03-16",
            "end_date": "2026-03-30",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_without_course(self):
        data = {
            "name": "test2",
            "start_date": "2026-02-01",
            "end_date": "2026-03-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_start_date(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "end_date": "2026-03-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_without_end_date(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-02-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_before_course_start_date(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2025-12-15",
            "end_date": "2026-02-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_end_date_after_course_end_date(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-02-01",
            "end_date": "2026-04-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_start_date_after_end_date(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-03-15",
            "end_date": "2026-02-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_with_overlapping_course_instructor(self):
        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-02-01",
            "end_date": "2026-02-15",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "The course instructore overlaps with an existing course instructore!",
            str(response.data),
        )

    def test_update_course_instructor_without_overlapping_itself(self):
        url = reverse(
            "course-instructor-detail",
            kwargs={"pk": self.course_instructor.pk},
        )

        data = {
            "name": "test2",
            "course": self.course.pk,
            "start_date": "2026-01-15",
            "end_date": "2026-03-15",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_update_course_instructor_with_start_date_before_new_course_start_date(
        self,
    ):
        new_course = Course.objects.create(
            name="Course 2",
            academic_term=self.academic_term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
        )

        url = reverse(
            "course-instructor-detail",
            kwargs={"pk": self.course_instructor.pk},
        )

        data = {
            "course": new_course.pk,
            "start_date": "2026-01-15",
            "end_date": "2026-03-15",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_course_instructor_with_end_date_after_new_course_end_date(self):
        new_course = Course.objects.create(
            name="Course 2",
            academic_term=self.academic_term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
        )

        url = reverse(
            "course-instructor-detail",
            kwargs={"pk": self.course_instructor.pk},
        )

        data = {
            "course": new_course.pk,
            "start_date": "2026-02-15",
            "end_date": "2026-05-15",
        }

        response = self.client.put(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
