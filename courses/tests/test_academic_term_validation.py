from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import AcademicTerm, Course
from organizations.models import School

AUTH_USER = get_user_model()


class AcademicTermValidationAPITest(APITestCase):
    def setUp(self):
        self.user = AUTH_USER.objects.create_user(
            username="admin",
            password="123",
            role="admin",
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.school = School.objects.create(
            name="school1", business_phone="02100000000"
        )

        self.term = AcademicTerm.objects.create(
            name="Term 1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )

        self.url = reverse("academic-term-list")

    def test_create_valid_academic_term(self):
        data = {
            "name": "Term 2",
            "start_date": "2026-04-01",
            "end_date": "2026-06-30",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_term_with_missing_start_date(self):
        data = {
            "name": "Term 2",
            "end_date": "2026-06-30",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_term_with_missing_end_date(self):
        data = {
            "name": "Term 2",
            "start_date": "2026-04-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_overlapping_term(self):
        data = {
            "name": "Overlapping Term",
            "start_date": "2026-03-01",
            "end_date": "2026-05-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The academic term overlaps with an existing term!",
            str(response.data),
        )

    def test_update_same_term_does_not_overlap_with_itself(self):
        url = reverse(
            "academic-term-detail",
            kwargs={"pk": self.term.pk},
        )

        data = {
            "name": "Updated Term",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_date_difference(self):
        data = {
            "name": "Invalid Term",
            "start_date": "2026-06-30",
            "end_date": "2026-06-01",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_starting_before_new_term_start_date(self):
        Course.objects.create(
            name="Course 1",
            academic_term=self.term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 2, 15),
        )

        url = reverse(
            "academic-term-detail",
            kwargs={"pk": self.term.pk},
        )

        data = {
            "name": "Updated Term",
            "start_date": "2026-02-01",
            "end_date": "2026-03-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "There is at least one course that starts before the selected start date!",
            str(response.data),
        )

    def test_course_ending_after_new_term_end_date(self):
        Course.objects.create(
            name="Course 1",
            academic_term=self.term,
            school=self.school,
            session_duration=90,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 4, 15),
        )

        url = reverse(
            "academic-term-detail",
            kwargs={"pk": self.term.pk},
        )

        data = {
            "name": "Updated Term",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "There is at least one course that ends after the selected end date!",
            str(response.data),
        )
