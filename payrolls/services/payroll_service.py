from decimal import Decimal
from datetime import date, timedelta

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.response import Response

from core.enums import State
from courses.enums import CourseSessionStatus, SessionDuration
from courses.models import CourseSession, AcademicTerm
from payrolls.enums import PayrollStatus
from payrolls.models import TeacherPayRate, Payroll
from reports.enums import ReportStatus
from reports.models import SessionReport


class PayrollService:
    @staticmethod
    @transaction.atomic
    def calculate_price(payroll):
        teacher = payroll.owner_user
        if not teacher:
            raise exceptions.ValidationError(
                {"owner_user": "Payroll owner user is required."}
            )
        year = payroll.year
        month = payroll.month
        target_date = date(year, month, 15)
        academic_term = AcademicTerm.objects.filter(
            start_date__lte=target_date,
            end_date__gte=target_date,
        ).first()
        if not academic_term:
            raise exceptions.ValidationError(
                "No academic term found for the selected payroll period."
            )

        if CourseSession.objects.filter(
            date__year=year,
            date__month=month,
            owner_user=teacher,
            status__in=[
                CourseSessionStatus.DRAFT,
                CourseSessionStatus.IN_PROGRESS,
            ],
        ).exists():
            raise exceptions.ValidationError(
                "In the selected month owner user has active sessions!"
            )

        completed_sessions_count = CourseSession.objects.filter(
            date__year=year,
            date__month=month,
            owner_user=teacher,
            status=CourseSessionStatus.COMPLETED,
        ).count()
        if completed_sessions_count == 0:
            payroll.status = PayrollStatus.NO_SESSION
            payroll.state = State.INACTIVE
            payroll.save(update_fields=["status", "state"])

            return payroll

        teacher_reports = SessionReport.objects.filter(
            course_session__date__year=year,
            course_session__date__month=month,
            owner_user=teacher,
        )

        if (
            teacher_reports.filter(status=ReportStatus.DRAFT).exists()
            or completed_sessions_count != teacher_reports.count()
        ):
            payroll.status = PayrollStatus.BANED
            payroll.state = State.INACTIVE
            payroll.save(update_fields=["status", "state"])

            return payroll

        approved_reports = teacher_reports.filter(status=ReportStatus.APPROVED)

        if not approved_reports.exists():
            wage = 0
        else:
            teacher_pay_rate = TeacherPayRate.objects.filter(
                academic_term=academic_term, owner_user=teacher, state=State.INACTIVE
            ).first()
            if not teacher_pay_rate:
                raise exceptions.ValidationError(
                    {
                        "owner_user": "An inactive pay rate for the owner user in the related term is required!"
                    }
                )
            reports_60 = approved_reports.filter(
                course_session__course__session_duration=SessionDuration.MINUTES_60
            ).count()
            reports_90 = approved_reports.filter(
                course_session__course__session_duration=SessionDuration.MINUTES_90
            ).count()
            reports_120 = approved_reports.filter(
                course_session__course__session_duration=SessionDuration.MINUTES_120
            ).count()

            total_delay_minutes = (
                teacher_reports.filter(
                    status=ReportStatus.APPROVED,
                    delay_minutes__gt=0,
                ).aggregate(total=Sum("delay_minutes"))["total"]
                or 0
            )
            print("90:", reports_90)
            print("60:", reports_60)
            print("120:", reports_120)
            wage = (
                (reports_60 * Decimal("0.7"))
                + reports_90
                + (reports_120 * Decimal("1.3"))
            ) * teacher_pay_rate.price_per_unit
            print("price_per_unit:", teacher_pay_rate.price_per_unit)
            print("profit:", wage)

            delay_hours = total_delay_minutes // 60
            print("delay_hours:", delay_hours)
            print(
                "penalty:",
                delay_hours * (teacher_pay_rate.price_per_unit * Decimal("0.01")),
            )

            wage -= delay_hours * (teacher_pay_rate.price_per_unit * Decimal("0.01"))
            print("total_price:", wage)
        if wage > 0:
            payroll.total_price = (
                wage * Decimal("1.1") if academic_term.is_summer else wage
            )
        else:
            payroll.total_price = 0
        payroll.status = PayrollStatus.CALCULATED
        payroll.state = State.INACTIVE
        payroll.save(update_fields=["total_price", "status", "state"])

        return payroll

    @staticmethod
    @transaction.atomic
    def bulk_create_and_calculate_price(user, teachers, year, month):
        result = {"success": {}, "failure": {}}
        for teacher in teachers:
            payroll = Payroll.objects.filter(
                owner_user=teacher, year=year, month=month
            ).first()
            if not payroll:
                payroll = Payroll.objects.create(
                    name=f"{teacher.get_full_name()}_{month}_{year}",
                    year=year,
                    month=month,
                    owner_user=teacher,
                    created_by=user,
                    created_at=timezone.now(),
                    updated_by=user,
                    updated_at=timezone.now(),
                    state=State.ACTIVE,
                    status=PayrollStatus.DRAFT,
                )
            try:
                payroll = PayrollService.calculate_price(payroll)
                result["success"][str(payroll.id)] = {
                    "total_price": payroll.total_price,
                }
            except exceptions.ValidationError as exc:
                result["failure"][str(payroll.id)] = exc.detail

        return result
