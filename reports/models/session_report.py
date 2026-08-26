from django.db import models

from core.models import BaseModel
from courses.models.course_session import CourseSession
from reports.enums import ReportStatus


# Create your models here.
class SessionReport(BaseModel):
    STATUS_CHOICES = ReportStatus
    DEFAULT_ACTIVE_STATUS = ReportStatus.DRAFT
    ACTIVE_STATUSES = {
        ReportStatus.DRAFT,
        ReportStatus.WAITING_FOR_REVIEW,
    }
    INACTIVE_STATUSES = {ReportStatus.APPROVED, ReportStatus.REJECTED}
    DELETED_STATUSES = {ReportStatus.DELETED}
    name = models.CharField(max_length=250)
    course_session = models.ForeignKey(CourseSession, on_delete=models.RESTRICT)
    reference_date_time = models.DateTimeField()
    last_submit_date_time = models.DateTimeField(blank=True, null=True)
    report_description = models.TextField()
    attendees = models.IntegerField()
    absentees = models.IntegerField()
    reviewer_description = models.TextField(blank=True, null=True)
    status = models.IntegerField(
        choices=list(ReportStatus.choices),
        default=ReportStatus.DRAFT,
    )
    is_delayed = models.BooleanField(default=False)
    delay_minutes = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course_session"],
                name="unique_report_per_course_session",
            )
        ]
