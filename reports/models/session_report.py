from django.db import models

from core.models import BaseModel
from courses.models.course_session import CourseSession
from reports.enums import ReportStatus


# Create your models here.
class SessionReport(BaseModel):
    STATUS_CHOICES = ReportStatus
    ACTIVE_STATUSES = {
        ReportStatus.DRAFT,
        ReportStatus.WAITING_FOR_EDIT,
        ReportStatus.WAITING_FOR_REVIEW,
    }
    INACTIVE_STATUSES = {ReportStatus.APPROVED, ReportStatus.REJECTED}
    DELETED_ACTIVE_STATUSES = {ReportStatus.DELETED}
    name = models.CharField(max_length=250)
    course_session = models.ForeignKey(CourseSession, on_delete=models.RESTRICT)
    reference_date = models.DateField()
    reference_time = models.TimeField()
    last_submit_date = models.DateField()
    last_submit_time = models.TimeField()
    report_description = models.TextField()
    attendees = models.IntegerField()
    absentees = models.IntegerField()
    reviewer_description = models.TextField()
    status = models.IntegerField(
        choices=list(ReportStatus.choices),
        default=ReportStatus.DRAFT,
    )
    is_delayed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
