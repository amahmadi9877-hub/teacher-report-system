from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from audits.decorators.audit import audit
from core.enums import State
from core.permissions import (
    IsEducationOfficer,
    IsAdmin,
    IsTeacher,
    IsOwner,
    IsResponsible,
)
from core.serializers import SetOwnerJustTeacherSerializer
from core.views import BaseModelViewSet
from reports.enums import ReportStatus
from reports.filters import SubmittedReportsFilter
from reports.models import SessionReport
from reports.serializers import (
    SessionReportSerializer,
    SessionReportDeactivateSerializer,
    MonthlyReportCountsSerializer,
    BulkDeactivateSerializer,
)


class SessionReportAPIModelViewSet(BaseModelViewSet):
    permission_classes = [IsAdmin]

    PERMISSIONS_BY_ACTION = {  # noqa: RUF012
        "list": [(IsEducationOfficer | IsAdmin)],
        "create": [(IsTeacher | IsAdmin)],
        "retrieve": [(IsEducationOfficer | (IsTeacher & IsOwner) | IsAdmin)],
        "update": [((IsTeacher & IsOwner & IsResponsible) | IsAdmin)],
        "partial_update": [((IsTeacher & IsOwner & IsResponsible) | IsAdmin)],
        "assign": [(IsEducationOfficer | IsAdmin)],
        "set_owner": [(IsEducationOfficer | IsAdmin)],
        "deactivate": [((IsEducationOfficer & IsResponsible) | IsAdmin)],
        "activate": [
            ((IsEducationOfficer & IsResponsible) | (IsTeacher & IsOwner) | IsAdmin)
        ],
        "submitted_reports": [(IsEducationOfficer | IsAdmin)],
        "monthly_report": [(IsTeacher | IsAdmin)],
        "bulk_deactivate": [(IsEducationOfficer | IsAdmin)],
    }

    FILTERSETS_BY_ACTION = {
        "submitted_reports": SubmittedReportsFilter,
    }

    model = SessionReport
    queryset = SessionReport.objects.all()
    serializer_class = SessionReportSerializer
    deactivate_serializer_class = SessionReportDeactivateSerializer
    set_owner_serializer_class = SetOwnerJustTeacherSerializer
    lookup_url_kwarg = "pk"

    @audit
    def perform_create(self, serializer):
        course_session = serializer.validated_data["course_session"]
        serializer.save(
            owner_user=course_session.owner_user,
            responsible_user=course_session.owner_user,
            reference_date_time=datetime.combine(
                course_session.date, course_session.end_time
            ),
        )
        super().perform_create(serializer)

    @audit
    def perform_update(self, serializer):
        if serializer.instance.status == ReportStatus.WAITING_FOR_REVIEW:
            raise exceptions.PermissionDenied(
                {"__all__": "Object is not editable becauese it is under review!"}
            )
        super().perform_update(serializer)
        course_session = serializer.validated_data.get("course_session")

        if course_session and course_session != serializer.instance.course_session:
            serializer.save(
                reference_date_time=datetime.combine(
                    course_session.date, course_session.end_time
                ),
                is_delayed=(
                    timezone.now()
                    - datetime.combine(course_session.date, course_session.end_time)
                    > timedelta(hours=48)
                ),
                last_submit_date_time=None,
                state=State.ACTIVE,
                status=ReportStatus.DRAFT,
            )

    @audit
    def perform_activate(self, serializer):
        print("99999999", serializer.validated_data["status"])
        if serializer.validated_data["status"] == ReportStatus.WAITING_FOR_REVIEW:
            obj = serializer.instance
            obj.last_submit_date_time = timezone.now()
            obj.is_delayed = timezone.now() - obj.reference_date_time > timedelta(
                hours=48
            )
            obj.save(
                update_fields=[
                    "last_submit_date_time",
                    "is_delayed",
                ]
            )
        super().perform_activate(serializer)

    @audit
    def perform_deactivate(self, serializer):
        return super().perform_deactivate(serializer)

    @audit
    def perform_assign(self, serializer):
        return super().perform_assign(serializer)

    @audit
    def perform_set_owner(self, serializer):
        return super().perform_set_owner(serializer)

    @action(
        detail=False,
        methods=["GET"],
        url_path="submitted-reports",
    )
    def submitted_reports(self, request):
        reports = SessionReport.objects.filter(status=ReportStatus.WAITING_FOR_REVIEW)
        reports = self.filter_queryset(reports)
        serializer = SessionReportSerializer(reports, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["GET"],
        url_path="monthly-report",
    )
    def monthly_report(self, request):
        year = request.query_params.get("year", timezone.now().year)
        month = request.query_params.get("month", timezone.now().month)

        reports = SessionReport.objects.filter(
            owner_user=request.user,
            reference_date_time__year=year,
            reference_date_time__month=month,
        )

        report_counts = {
            "draft": reports.filter(status=ReportStatus.DRAFT).count(),
            "submitted": reports.filter(status=ReportStatus.WAITING_FOR_REVIEW).count(),
            "approved": reports.filter(status=ReportStatus.APPROVED).count(),
            "rejected": reports.filter(status=ReportStatus.REJECTED).count(),
        }

        serializer = MonthlyReportCountsSerializer(report_counts)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="bulk-deactivate",
    )
    def bulk_deactivate(self, request):
        serializer = BulkDeactivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_ids = serializer.validated_data["ids"]
        status_value = serializer.validated_data["status"]

        reports = SessionReport.objects.filter(
            id__in=report_ids,
        )
        error_ids = []
        approved_ids = []
        for report in reports:
            if (
                report.status == ReportStatus.DRAFT
                or report.responsible_user != request.owner
            ):
                error_ids.append(report.id)
                continue
            serializer = self.deactivate_serializer_class(
                instance=report,
                data={
                    "status": status_value,
                    "reviewer_description": (
                        "report is approved!"
                        if status_value == ReportStatus.APPROVED
                        else "report is rejected!"
                    ),
                },
            )
            serializer.is_valid(raise_exception=True)

            self.perform_deactivate(serializer)
            approved_ids.append(report.id)

        return Response(
            {
                "detail": f"Records deactivated successfully: {approved_ids}",
                "fails_ids": error_ids,
            },
            status=status.HTTP_200_OK,
        )
