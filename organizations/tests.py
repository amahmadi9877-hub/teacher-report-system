from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.urls import reverse

from organizations.models import School

AUTH_MODEL = get_user_model()


class SchoolAPITest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="schooltest1", business_phone="02100000000"
        )
        self.admin = AUTH_MODEL(username=1, role="admin")
        self.admin.set_password("1")
        self.admin.save()
        self.teacher = AUTH_MODEL(username=2, role="teacher")
        self.teacher.set_password("1")
        self.teacher.save()
        self.education_officer = AUTH_MODEL(username=3, role="education_officer")
        self.education_officer.set_password("1")
        self.education_officer.save()
        self.finance_officer = AUTH_MODEL(username=4, role="finance_officer")
        self.finance_officer.set_password("1")
        self.finance_officer.save()

        self.list_url = reverse("school-list")
        self.detail_url = reverse("school-detail", kwargs={"pk": self.school.pk})

    def authenticate_user(self, user):
        self.client = APIClient()
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # --------unauthenticated user tests------------

    def test_unauthenticated_user_access_school_list_error(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_create_school_error(self):
        response = self.client.post(
            self.list_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_check_school_error(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_update_school_error(self):
        response = self.client.put(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_partial_update_school_error(self):
        response = self.client.patch(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_partial_delete_school_error(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------authenticated education officer user tests------------

    def test_authenticated_education_officer_access_school_list(self):
        self.authenticate_user(self.education_officer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_education_officer_create_school(self):
        self.authenticate_user(self.education_officer)
        response = self.client.post(
            self.list_url,
            {
                "name": "schooltest1",
                "business_phone": "02100000001",
                "state": -1,
                "status": -1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_education_officer_check_school(self):
        self.authenticate_user(self.education_officer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_education_officer_update_school(self):
        self.authenticate_user(self.education_officer)
        response = self.client.put(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_education_officer_partial_update_school(self):
        self.authenticate_user(self.education_officer)
        response = self.client.patch(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_education_officer_partial_delete_school(self):
        self.authenticate_user(self.education_officer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --------authenticated admin user tests------------

    def test_authenticated_admin_access_school_list(self):
        self.authenticate_user(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_admin_create_school(self):
        self.authenticate_user(self.admin)
        response = self.client.post(
            self.list_url,
            {
                "name": "schooltest1",
                "business_phone": "02100000001",
                "state": -1,
                "status": -1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_admin_check_school(self):
        self.authenticate_user(self.admin)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_admin_update_school(self):
        self.authenticate_user(self.admin)
        response = self.client.put(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_admin_partial_update_school(self):
        self.authenticate_user(self.admin)
        response = self.client.patch(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_admin_partial_delete_school(self):
        self.authenticate_user(self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --------authenticated teacher user tests------------
    def test_authenticated_teacher_access_school_list_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_teacher_create_school_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.post(
            self.list_url,
            {
                "name": "schooltest1",
                "business_phone": "02100000001",
                "state": -1,
                "status": -1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_teacher_check_school_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_teacher_update_school_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.put(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_teacher_partial_update_school_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.patch(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_teacher_partial_delete_school_error(self):
        self.authenticate_user(self.teacher)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------authenticated finance officer user tests------------
    def test_authenticated_finance_officer_access_school_list_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_finance_officer_create_school_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.post(
            self.list_url,
            {
                "name": "schooltest1",
                "business_phone": "02100000001",
                "state": -1,
                "status": -1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_finance_officer_check_school_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_finance_officer_update_school_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.put(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_finance_officer_partial_update_school_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.patch(
            self.detail_url, {"name": "schooltest1", "business_phone": "02100000001"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_finance_officer_partial_delete_school_error(self):
        self.authenticate_user(self.finance_officer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
