from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.urls import reverse

from courses.models import AcademicTerm, Course
from organizations.models import School

AUTH_MODEL = get_user_model()


class CourseAPITest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="school1", business_phone="02100000000"
        )

        self.academic_term = AcademicTerm.objects.create(
            name="term1",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            status=-1,
            state=-1,
        )

        self.course = Course.objects.create(
            name="course1",
            school=self.school,
            academic_term=self.academic_term,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            status=-1,
            state=-1,
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

        self.academic_term_list_url = reverse("academic-term-list")
        self.academic_term_detail_url = reverse(
            "academic-term-detail", kwargs={"pk": self.academic_term.pk}
        )
        self.course_list_url = reverse("course-list")
        self.course_detail_url = reverse("course-detail", kwargs={"pk": self.course.pk})

    def authenticate_user(self, user):
        self.client = APIClient()
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # --------unauthenticated user course tests------------

    # def test_unauthenticated_user_access_course_list_error(self):
    #     response = self.client.get(self.course_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_create_course_error(self):
    #     response = self.client.post(
    #         self.course_list_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_check_course_error(self):
    #     response = self.client.get(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_update_course_error(self):
    #     response = self.client.put(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_partial_update_course_error(self):
    #     response = self.client.patch(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_partial_delete_course_error(self):
    #     response = self.client.delete(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # --------authenticated education officer user course tests------------

    # def test_authenticated_education_officer_access_course_list(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.get(self.course_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_create_course(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.post(
    #         self.course_list_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date(),
    #             "status": -1,
    #             "state": -1,
    #             "session_count": 0,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_authenticated_education_officer_check_course(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.get(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_update_course(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.put(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_partial_update_course(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.patch(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "state": -1,
    #             "status": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_partial_delete_course(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.delete(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # # --------authenticated admin user course tests------------

    # def test_authenticated_admin_access_course_list(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.get(self.course_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_create_course(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.post(
    #         self.course_list_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_authenticated_admin_check_course(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.get(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_update_course(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.put(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_partial_update_course(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.patch(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_partial_delete_course(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.delete(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # # --------authenticated teacher user course tests------------
    # def test_authenticated_teacher_access_course_list_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.get(self.course_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_create_course_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.post(
    #         self.course_list_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_check_course_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.get(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_update_course_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.put(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_partial_update_course_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.patch(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_partial_delete_course_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.delete(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # # --------authenticated finance officer user course tests------------
    # def test_authenticated_finance_officer_access_course_list_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.get(self.course_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_create_course_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.post(
    #         self.course_list_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_check_course_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.get(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_update_course_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.put(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_partial_update_course_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.patch(
    #         self.course_detail_url,
    #         {
    #             "name": "coursetest1",
    #             "school": self.school.id,
    #             "academic_term": self.academic_term.id,
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_partial_delete_course_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.delete(self.course_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    ##===============================================================================================

    ##-------------------------------------Academic Term---------------------------------------------

    ##===============================================================================================

    # --------unauthenticated user academic_term tests------------

    # def test_unauthenticated_user_access_academic_term_list_error(self):
    #     response = self.client.get(self.academic_term_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_create_academic_term_error(self):
    #     response = self.client.post(
    #         self.academic_term_list_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_check_academic_term_error(self):
    #     response = self.client.get(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_update_academic_term_error(self):
    #     response = self.client.put(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_partial_update_academic_term_error(self):
    #     response = self.client.patch(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_unauthenticated_user_partial_delete_academic_term_error(self):
    #     self.course.delete()
    #     response = self.client.delete(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # # --------authenticated education officer user academic_term tests------------

    # def test_authenticated_education_officer_access_academic_term_list(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.get(self.academic_term_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_create_academic_term(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.post(
    #         self.academic_term_list_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date(),
    #             "status": -1,
    #             "state": -1,
    #             "session_count": 0,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_authenticated_education_officer_check_academic_term(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.get(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_update_academic_term(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.put(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_partial_update_academic_term(self):
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.patch(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "state": -1,
    #             "status": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_education_officer_partial_delete_academic_term(self):
    #     self.course.delete()
    #     self.authenticate_user(self.education_officer)
    #     response = self.client.delete(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # # --------authenticated admin user academic_term tests------------

    # def test_authenticated_admin_access_academic_term_list(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.get(self.academic_term_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_create_academic_term(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.post(
    #         self.academic_term_list_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_authenticated_admin_check_academic_term(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.get(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_update_academic_term(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.put(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_partial_update_academic_term(self):
    #     self.authenticate_user(self.admin)
    #     response = self.client.patch(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_authenticated_admin_partial_delete_academic_term(self):
    #     self.course.delete()
    #     self.authenticate_user(self.admin)
    #     response = self.client.delete(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # # --------authenticated teacher user academic_term tests------------
    # def test_authenticated_teacher_access_academic_term_list_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.get(self.academic_term_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_create_academic_term_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.post(
    #         self.academic_term_list_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_check_academic_term_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.get(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_update_academic_term_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.put(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_partial_update_academic_term_error(self):
    #     self.authenticate_user(self.teacher)
    #     response = self.client.patch(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_teacher_partial_delete_academic_term_error(self):
    #     self.course.delete()
    #     self.authenticate_user(self.teacher)
    #     response = self.client.delete(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # # --------authenticated finance officer user academic_term tests------------
    # def test_authenticated_finance_officer_access_academic_term_list_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.get(self.academic_term_list_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_create_academic_term_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.post(
    #         self.academic_term_list_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_check_academic_term_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.get(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_update_academic_term_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.put(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_partial_update_academic_term_error(self):
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.patch(
    #         self.academic_term_detail_url,
    #         {
    #             "name": "academic_termtest1",
    #             "start_date": timezone.now().date(),
    #             "end_date": timezone.now().date() + timedelta(days=30),
    #             "status": -1,
    #             "state": -1,
    #         },
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_authenticated_finance_officer_partial_delete_academic_term_error(self):
    #     self.course.delete()
    #     self.authenticate_user(self.finance_officer)
    #     response = self.client.delete(self.academic_term_detail_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
