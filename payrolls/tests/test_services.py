from datetime import date, datetime, time
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import exceptions

from accounts.models import User
from courses.enums import CourseSessionStatus, SessionDuration
from courses.models import AcademicTerm, Course, CourseSession
from organizations.models import School
from payrolls.enums import PayrollStatus
from payrolls.models import Payroll, TeacherPayRate
from payrolls.services import PayrollService
from reports.enums import ReportStatus
from reports.models import SessionReport

from core.enums import State


class PayrollServiceTest(TestCase):
    def setUp(self):
        self.teacher = self.create_teacher("teacher1")
        self.teacher2 = self.create_teacher("teacher2")

        self.finance_user = self.create_user(
            username="finance",
            role="finance_officer",
        )

        self.term = self.create_academic_term()

        self.school = School.objects.create(
            name="Test School",
            business_phone="09120000001",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_user(self, username, role="teacher"):
        return User.objects.create_user(
            username=username,
            password="Test123456",
            first_name="Test",
            last_name="User",
            role=role,
            phone_number="09120000002",
            backup_phone_number="09120000003",
        )

    def create_teacher(self, username):
        return self.create_user(username=username, role="teacher")

    def create_academic_term(
        self,
        *,
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
        is_summer=False,
    ):
        return AcademicTerm.objects.create(
            name="Test Term",
            start_date=start_date,
            end_date=end_date,
            is_summer=is_summer,
            state=State.ACTIVE,
        )

    def create_course(
        self,
        *,
        duration=SessionDuration.MINUTES_60,
        academic_term=None,
    ):
        return Course.objects.create(
            name="Test Course",
            academic_term=academic_term or self.term,
            school=self.school,
            session_count=10,
            session_duration=duration,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 31),
        )

    def create_session(
        self,
        *,
        teacher=None,
        course=None,
        status=CourseSessionStatus.COMPLETED,
        day=10,
        duration=None,
    ):
        teacher = teacher or self.teacher

        course = course or self.create_course(
            duration=duration or SessionDuration.MINUTES_60
        )

        return CourseSession.objects.create(
            name=f"Session {day}",
            date=date(2026, 8, day),
            week_day=0,
            start_time=time(10, 0),
            end_time=time(11, 0),
            course=course,
            course_schedule=None,
            owner_user=teacher,
            status=status,
        )

    def create_report(
        self,
        *,
        course_session,
        teacher=None,
        status=ReportStatus.APPROVED,
        delay_minutes=0,
    ):
        teacher = teacher or course_session.owner_user

        return SessionReport.objects.create(
            name=f"Report {course_session.id}",
            course_session=course_session,
            reference_date_time=timezone.make_aware(
                datetime(2026, 8, course_session.date.day, 11, 0)
            ),
            last_submit_date_time=timezone.make_aware(
                datetime(2026, 8, course_session.date.day, 12, 0)
            ),
            report_description="Test report",
            attendees=10,
            absentees=0,
            reviewer_description="Approved",
            status=status,
            is_delayed=delay_minutes > 0,
            delay_minutes=delay_minutes,
            owner_user=teacher,
        )

    def create_payroll(
        self,
        *,
        teacher=None,
        year=2026,
        month=8,
        status=PayrollStatus.DRAFT,
    ):
        teacher = teacher or self.teacher

        return Payroll.objects.create(
            name=f"{teacher.get_full_name()}_{month}_{year}",
            year=year,
            month=month,
            owner_user=teacher,
            total_price=Decimal("0"),
            status=status,
            state=State.ACTIVE,
        )

    def create_pay_rate(
        self,
        *,
        teacher=None,
        academic_term=None,
        price_per_unit="1000000",
    ):
        return TeacherPayRate.objects.create(
            name="Teacher Pay Rate",
            academic_term=academic_term or self.term,
            owner_user=teacher or self.teacher,
            price_per_unit=Decimal(price_per_unit),
            state=State.INACTIVE,
        )

    # ------------------------------------------------------------------
    # calculate_price
    # ------------------------------------------------------------------

    def test_calculate_price_fails_when_owner_user_is_missing(self):
        payroll = self.create_payroll()
        payroll.owner_user = None
        payroll.save(update_fields=["owner_user"])

        with self.assertRaises(exceptions.ValidationError) as context:
            PayrollService.calculate_price(payroll)

        self.assertEqual(
            str(context.exception.detail["owner_user"]),
            "Payroll owner user is required.",
        )

    def test_calculate_price_fails_when_academic_term_does_not_exist(self):
        payroll = self.create_payroll(
            year=2027,
            month=1,
        )

        with self.assertRaises(exceptions.ValidationError) as context:
            PayrollService.calculate_price(payroll)

        self.assertIn(
            "No academic term found",
            str(context.exception.detail),
        )

    def test_calculate_price_fails_when_teacher_has_active_sessions(self):
        payroll = self.create_payroll()

        self.create_session(
            status=CourseSessionStatus.DRAFT,
        )

        with self.assertRaises(exceptions.ValidationError) as context:
            PayrollService.calculate_price(payroll)

        self.assertIn(
            "active sessions",
            str(context.exception.detail),
        )

    def test_calculate_price_sets_no_session_when_teacher_has_no_completed_sessions(
        self,
    ):
        payroll = self.create_payroll()

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(result.status, PayrollStatus.NO_SESSION)
        self.assertEqual(result.state, State.INACTIVE)
        self.assertEqual(result.total_price, Decimal("0"))

    def test_calculate_price_sets_baned_when_reports_are_missing(self):
        payroll = self.create_payroll()

        self.create_session(
            status=CourseSessionStatus.COMPLETED,
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(result.status, PayrollStatus.BANED)
        self.assertEqual(result.state, State.INACTIVE)

    def test_calculate_price_sets_baned_when_a_report_is_draft(self):
        payroll = self.create_payroll()

        session1 = self.create_session(
            status=CourseSessionStatus.COMPLETED,
            day=10,
        )
        session2 = self.create_session(
            status=CourseSessionStatus.COMPLETED,
            day=11,
        )

        self.create_report(
            course_session=session1,
            status=ReportStatus.APPROVED,
        )
        self.create_report(
            course_session=session2,
            status=ReportStatus.DRAFT,
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(result.status, PayrollStatus.BANED)
        self.assertEqual(result.state, State.INACTIVE)

    def test_calculate_price_returns_zero_when_no_report_is_approved(self):
        """
        Boundary case required by the specification:
        teacher has sessions/reports but no approved report.
        """

        payroll = self.create_payroll()

        session1 = self.create_session(
            status=CourseSessionStatus.COMPLETED,
            day=10,
        )
        session2 = self.create_session(
            status=CourseSessionStatus.COMPLETED,
            day=11,
        )

        self.create_report(
            course_session=session1,
            status=ReportStatus.WAITING_FOR_REVIEW,
        )
        self.create_report(
            course_session=session2,
            status=ReportStatus.REJECTED,
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(result.total_price, Decimal("0"))
        self.assertEqual(result.status, PayrollStatus.CALCULATED)
        self.assertEqual(result.state, State.INACTIVE)

    def test_calculate_price_fails_when_pay_rate_does_not_exist(self):
        payroll = self.create_payroll()

        session = self.create_session(
            status=CourseSessionStatus.COMPLETED,
        )

        self.create_report(
            course_session=session,
            status=ReportStatus.APPROVED,
        )

        with self.assertRaises(exceptions.ValidationError) as context:
            PayrollService.calculate_price(payroll)

        self.assertIn(
            "inactive pay rate",
            str(context.exception.detail),
        )

    def test_calculate_price_for_60_minute_session(self):
        payroll = self.create_payroll()

        course = self.create_course(
            duration=SessionDuration.MINUTES_60,
        )

        session = self.create_session(
            course=course,
            status=CourseSessionStatus.COMPLETED,
        )

        self.create_report(course_session=session)

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        expected = Decimal("700000")

        self.assertEqual(result.total_price, expected)
        self.assertEqual(result.status, PayrollStatus.CALCULATED)
        self.assertEqual(result.state, State.INACTIVE)

    def test_calculate_price_for_90_minute_session(self):
        payroll = self.create_payroll()

        course = self.create_course(
            duration=SessionDuration.MINUTES_90,
        )

        session = self.create_session(
            course=course,
            status=CourseSessionStatus.COMPLETED,
        )

        self.create_report(course_session=session)

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(
            result.total_price,
            Decimal("1000000"),
        )

    def test_calculate_price_for_120_minute_session(self):
        payroll = self.create_payroll()

        course = self.create_course(
            duration=SessionDuration.MINUTES_120,
        )

        session = self.create_session(
            course=course,
            status=CourseSessionStatus.COMPLETED,
        )

        self.create_report(course_session=session)

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(
            result.total_price,
            Decimal("1300000"),
        )

    def test_calculate_price_for_mixed_session_durations(self):
        payroll = self.create_payroll()

        course_60 = self.create_course(
            duration=SessionDuration.MINUTES_60,
        )
        course_90 = self.create_course(
            duration=SessionDuration.MINUTES_90,
        )
        course_120 = self.create_course(
            duration=SessionDuration.MINUTES_120,
        )

        session_60 = self.create_session(
            course=course_60,
            day=10,
        )
        session_90 = self.create_session(
            course=course_90,
            day=11,
        )
        session_120 = self.create_session(
            course=course_120,
            day=12,
        )

        self.create_report(course_session=session_60)
        self.create_report(course_session=session_90)
        self.create_report(course_session=session_120)

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        # 0.7 + 1 + 1.3 = 3 units
        self.assertEqual(
            result.total_price,
            Decimal("3000000"),
        )

    def test_delay_of_one_hour_deducts_one_percent(self):
        payroll = self.create_payroll()

        session = self.create_session(
            duration=SessionDuration.MINUTES_90,
        )

        self.create_report(
            course_session=session,
            delay_minutes=60,
        )

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        # 1,000,000 - 1%
        self.assertEqual(
            result.total_price,
            Decimal("990000"),
        )

    def test_multiple_hours_of_delay_deduct_multiple_percent(self):
        payroll = self.create_payroll()

        session = self.create_session(
            duration=SessionDuration.MINUTES_90,
        )

        self.create_report(
            course_session=session,
            delay_minutes=125,
        )

        self.create_pay_rate(
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        # 2 complete hours => 2%
        self.assertEqual(
            result.total_price,
            Decimal("980000"),
        )

    def test_summer_term_increases_final_price_by_ten_percent(self):
        summer_term = self.create_academic_term(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            is_summer=True,
        )

        payroll = self.create_payroll(
            year=2026,
            month=9,
        )

        course = self.create_course(
            academic_term=summer_term,
            duration=SessionDuration.MINUTES_90,
        )

        session = self.create_session(
            course=course,
            day=10,
        )

        session.date = date(2026, 9, 10)
        session.save(update_fields=["date"])

        self.create_report(course_session=session)

        self.create_pay_rate(
            academic_term=summer_term,
            price_per_unit="1000000",
        )

        result = PayrollService.calculate_price(payroll)

        result.refresh_from_db()

        self.assertEqual(
            result.total_price,
            Decimal("1100000"),
        )

    # ------------------------------------------------------------------
    # bulk_create_and_calculate_price
    # ------------------------------------------------------------------

    def test_bulk_create_creates_payroll_for_teachers(self):
        result = PayrollService.bulk_create_and_calculate_price(
            self.finance_user,
            [self.teacher],
            2026,
            8,
        )

        payroll = Payroll.objects.get(
            owner_user=self.teacher,
            year=2026,
            month=8,
        )

        self.assertIn(
            str(payroll.id),
            result["success"],
        )

        self.assertEqual(
            payroll.created_by,
            self.finance_user,
        )

    def test_bulk_create_uses_existing_payroll(self):
        payroll = self.create_payroll(
            teacher=self.teacher,
        )

        result = PayrollService.bulk_create_and_calculate_price(
            self.finance_user,
            [self.teacher],
            2026,
            8,
        )

        self.assertEqual(
            Payroll.objects.filter(
                owner_user=self.teacher,
                year=2026,
                month=8,
            ).count(),
            1,
        )

        self.assertIn(
            str(payroll.id),
            result["success"],
        )

    def test_bulk_create_puts_validation_error_in_failure(self):
        """
        Teacher has no AcademicTerm for the requested month.
        calculate_price raises ValidationError.
        bulk method catches it and puts it in failure.
        """

        result = PayrollService.bulk_create_and_calculate_price(
            self.finance_user,
            [self.teacher],
            2027,
            1,
        )

        payroll = Payroll.objects.get(
            owner_user=self.teacher,
            year=2027,
            month=1,
        )

        self.assertIn(
            str(payroll.id),
            result["failure"],
        )

        self.assertNotIn(
            str(payroll.id),
            result["success"],
        )

    def test_bulk_create_handles_multiple_teachers(self):
        result = PayrollService.bulk_create_and_calculate_price(
            self.finance_user,
            [self.teacher, self.teacher2],
            2026,
            8,
        )

        self.assertEqual(
            Payroll.objects.filter(
                year=2026,
                month=8,
            ).count(),
            2,
        )

        self.assertEqual(
            len(result["success"]),
            2,
        )
