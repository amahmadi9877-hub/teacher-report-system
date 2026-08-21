from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from core.enums import State
from courses.enums import CourseSessionStatus
from courses.models import Course, CourseSession, AcademicTerm
from reports.enums import ReportStatus
from reports.models import SessionReport
from organizations.models import School

User = get_user_model()


class SessionReportAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin",
            password="123456",
            role="admin",
        )

        cls.education_officer = User.objects.create_user(
            username="education",
            password="123456",
            role="education_officer",
        )

        cls.teacher1 = User.objects.create_user(
            username="teacher1",
            password="123456",
            role="teacher",
        )

        cls.teacher2 = User.objects.create_user(
            username="teacher2",
            password="123456",
            role="teacher",
        )

        cls.school = School.objects.create(name="school1", business_phone="02100000000")

        cls.academic_term = AcademicTerm.objects.create(
            name="term1",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            status=1,
            state=1,
        )

        cls.course1 = Course.objects.create(
            name="Python",
            school=cls.school,
            academic_term=cls.academic_term,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            session_duration=90,
            status=1,
            state=1,
        )
        cls.course2 = Course.objects.create(
            name="Django",
            school=cls.school,
            academic_term=cls.academic_term,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            session_duration=90,
            status=1,
            state=1,
        )

    def create_course_session(
        self,
        course,
        teacher,
        date=None,
        status=CourseSessionStatus.COMPLETED,
        state=State.INACTIVE,
    ):

        return CourseSession.objects.create(
            name=f"session {course.name} on {date}",
            course=course,
            date=date or timezone.now().date(),
            week_day=0,
            start_time="10:00",
            end_time="11:30",
            status=status,
            state=state,
            owner_user=teacher,
        )

    def create_report(
        self,
        course_session,
        teacher=None,
        responsible=None,
        status=ReportStatus.DRAFT,
        reference_date_time=None,
    ):
        teacher = teacher or course_session.owner_user
        responsible = responsible or teacher

        reference_date_time = reference_date_time or timezone.make_aware(
            timezone.datetime.combine(
                course_session.date,
                course_session.end_time,
            )
        )

        return SessionReport.objects.create(
            name="Session report",
            course_session=course_session,
            reference_date_time=reference_date_time,
            report_description="Python basics",
            attendees=10,
            absentees=2,
            owner_user=teacher,
            responsible_user=responsible,
            status=status,
            state=State.ACTIVE,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def list_url(self):
        return reverse("session-report-list")

    def detail_url(self, report):
        return reverse(
            "session-report-detail",
            kwargs={"pk": report.pk},
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def test_teacher_can_create_report_for_own_course_session(self):
        session = self.create_course_session(self.course1, self.teacher1)

        self.authenticate(self.teacher1)

        response = self.client.post(
            self.list_url(),
            {
                "name": "Python session report",
                "course_session": session.id,
                "report_description": "Introduction to Python",
                "attendees": 10,
                "absentees": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(course_session=session)

        self.assertEqual(
            report.owner_user,
            self.teacher1,
        )

        self.assertEqual(
            report.responsible_user,
            self.teacher1,
        )

        self.assertEqual(
            report.status,
            ReportStatus.DRAFT,
        )

        self.assertEqual(
            report.reference_date_time.date(),
            session.date,
        )

        self.assertEqual(
            report.reference_date_time.time(),
            session.end_time,
        )

    def test_teacher_cannot_create_report_for_other_teacher_session(self):
        session = self.create_course_session(self.course2, self.teacher2)

        self.authenticate(self.teacher1)

        response = self.client.post(
            self.list_url(),
            {
                "name": "Unauthorized report",
                "course_session": session.id,
                "report_description": "Unauthorized",
                "attendees": 10,
                "absentees": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(SessionReport.objects.filter(course_session=session).exists())

    def test_teacher_cannot_create_report_for_uncompleted_session(self):
        session = self.create_course_session(
            self.course1,
            self.teacher1,
            status=CourseSessionStatus.DRAFT,
        )

        self.authenticate(self.teacher1)

        response = self.client.post(
            self.list_url(),
            {
                "name": "Report",
                "course_session": session.id,
                "report_description": "Test",
                "attendees": 10,
                "absentees": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_create_second_report_for_same_session(self):
        session = self.create_course_session(self.course1, self.teacher1)

        self.create_report(session)

        self.authenticate(self.teacher1)

        response = self.client.post(
            self.list_url(),
            {
                "name": "Second report",
                "course_session": session.id,
                "report_description": "Test",
                "attendees": 10,
                "absentees": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ==========================================================
    # 48 HOURS
    # ==========================================================

    def test_report_is_not_delayed_when_submitted_before_48_hours(self):
        reference = timezone.now() - timedelta(hours=47)

        session = self.create_course_session(
            self.course1,
            self.teacher1,
            date=reference.date(),
        )

        self.authenticate(self.teacher1)

        report = self.create_report(
            session,
            reference_date_time=reference,
        )

        self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.WAITING_FOR_REVIEW,
            },
        )

        report.refresh_from_db()

        self.assertFalse(report.is_delayed)

    def test_report_is_delayed_when_submitted_after_48_hours(self):
        reference = timezone.now() - timedelta(hours=49)

        session = self.create_course_session(
            self.course1,
            self.teacher1,
            date=reference.date(),
        )

        self.authenticate(self.teacher1)

        report = self.create_report(
            session,
            reference_date_time=reference,
        )

        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.WAITING_FOR_REVIEW,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertTrue(report.is_delayed)

        self.assertIsNotNone(report.last_submit_date_time)

    # ==========================================================
    # UPDATE
    # ==========================================================

    def test_teacher_can_update_own_draft_report(self):
        session = self.create_course_session(self.course1, self.teacher1)
        report = self.create_report(session)

        self.authenticate(self.teacher1)

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Updated description",
                "attendees": 12,
                "absentees": 0,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.report_description,
            "Updated description",
        )

        self.assertEqual(
            report.attendees,
            12,
        )

    def test_report_cannot_be_updated_while_waiting_for_review(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )

        self.authenticate(self.teacher1)

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Modified",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_cannot_update_other_teacher_report(self):
        session = self.create_course_session(self.course2, self.teacher2)

        report = self.create_report(
            session,
            teacher=self.teacher2,
        )

        self.authenticate(self.teacher1)

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Unauthorized",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # APPROVE / REJECT
    # ==========================================================

    def test_education_officer_can_approve_report(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            responsible=self.education_officer,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )

        self.authenticate(self.education_officer)

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.APPROVED,
                "reviewer_description": "Approved.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.APPROVED,
        )

        self.assertEqual(
            report.state,
            State.INACTIVE,
        )

        self.assertEqual(
            report.reviewer_description,
            "Approved.",
        )

    def test_education_officer_can_reject_report_with_reason(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            responsible=self.education_officer,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )

        self.authenticate(self.education_officer)

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.REJECTED,
                "reviewer_description": "Attendance numbers are incorrect.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.REJECTED,
        )

        self.assertEqual(
            report.reviewer_description,
            "Attendance numbers are incorrect.",
        )

    def test_rejection_requires_reviewer_description(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            responsible=self.education_officer,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )

        self.authenticate(self.education_officer)

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.REJECTED,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.WAITING_FOR_REVIEW,
        )

    # ==========================================================
    # TEACHER CANNOT APPROVE
    # ==========================================================

    def test_teacher_cannot_approve_own_report(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            responsible=self.education_officer,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )

        self.authenticate(self.teacher1)

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.APPROVED,
                "reviewer_description": "Approved by teacher",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.WAITING_FOR_REVIEW,
        )

    # ==========================================================
    # EDUCATION OFFICER CANNOT EDIT CONTENT
    # ==========================================================

    def test_education_officer_cannot_edit_report_content(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            responsible=self.education_officer,
            status=ReportStatus.DRAFT,
        )

        old_description = report.report_description
        old_attendees = report.attendees

        self.authenticate(self.education_officer)

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Changed by education officer",
                "attendees": 100,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.report_description,
            old_description,
        )

        self.assertEqual(
            report.attendees,
            old_attendees,
        )

    # ==========================================================
    # REJECT -> EDIT -> RESUBMIT
    # ==========================================================

    def test_rejected_report_can_be_edited_and_resubmitted(self):
        session = self.create_course_session(self.course1, self.teacher1)

        report = self.create_report(
            session,
            status=ReportStatus.REJECTED,
        )

        report.reviewer_description = "Please correct attendance."
        report.save()
        self.authenticate(self.teacher1)
        response = self.client.post(
            reverse(
                "session-report-assign",
                kwargs={"pk": report.pk},
            ),
            {
                "user_id": self.teacher1.id,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.authenticate(self.teacher1)

        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.DRAFT,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Corrected report",
                "attendees": 11,
                "absentees": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.report_description,
            "Corrected report",
        )

        self.assertEqual(
            report.attendees,
            11,
        )

        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.WAITING_FOR_REVIEW,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.WAITING_FOR_REVIEW,
        )

        self.assertIsNotNone(report.last_submit_date_time)

    # ==========================================================
    # COMPLETE LIFECYCLE
    # ==========================================================

    def test_complete_report_lifecycle(self):
        session = self.create_course_session(self.course1, self.teacher1)

        # 1. Teacher creates report
        self.authenticate(self.teacher1)

        response = self.client.post(
            self.list_url(),
            {
                "name": "Python session",
                "course_session": session.id,
                "report_description": "Initial report",
                "attendees": 10,
                "absentees": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(course_session=session)

        self.assertEqual(
            report.status,
            ReportStatus.DRAFT,
        )

        # 2. Teacher submits
        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.WAITING_FOR_REVIEW,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.WAITING_FOR_REVIEW,
        )

        # 3. Education officer rejects

        self.authenticate(self.education_officer)
        response = self.client.post(
            reverse(
                "session-report-assign",
                kwargs={"pk": report.pk},
            ),
            {
                "user_id": self.education_officer.id,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.REJECTED,
                "reviewer_description": "Please correct attendance.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.REJECTED,
        )

        # 4. Teacher edits
        response = self.client.post(
            reverse(
                "session-report-assign",
                kwargs={"pk": report.pk},
            ),
            {
                "user_id": self.teacher1.id,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.authenticate(self.teacher1)

        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.DRAFT,
            },
        )

        response = self.client.patch(
            self.detail_url(report),
            {
                "report_description": "Corrected report",
                "attendees": 11,
                "absentees": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # 5. Teacher submits again
        response = self.client.post(
            reverse(
                "session-report-activate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.WAITING_FOR_REVIEW,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.WAITING_FOR_REVIEW,
        )

        # 6. Education officer approves
        self.authenticate(self.education_officer)
        response = self.client.post(
            reverse(
                "session-report-assign",
                kwargs={"pk": report.pk},
            ),
            {
                "user_id": self.education_officer.id,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            reverse(
                "session-report-deactivate",
                kwargs={"pk": report.pk},
            ),
            {
                "status": ReportStatus.APPROVED,
                "reviewer_description": "Approved after correction.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            ReportStatus.APPROVED,
        )
