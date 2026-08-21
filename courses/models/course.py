from django.db import models

from core.models import BaseModel
from courses.enums import CourseStatus, SessionDuration


# Create your models here.
class Course(BaseModel):
    STATUS_CHOICES = CourseStatus
    DEFAULT_ACTIVE_STATUS = CourseStatus.DRAFT
    ACTIVE_STATUSES = {
        CourseStatus.DRAFT,
        CourseStatus.IN_PROGRESS,
        CourseStatus.SCHEDULING,
        CourseStatus.SCHEDULED,
    }
    INACTIVE_STATUSES = {CourseStatus.COMPLETED, CourseStatus.CANCELED}
    DELETED_STATUSES = {CourseStatus.DELETED}
    name = models.CharField(max_length=100)
    academic_term = models.ForeignKey("courses.AcademicTerm", on_delete=models.RESTRICT)
    school = models.ForeignKey("organizations.School", on_delete=models.RESTRICT)
    session_count = models.IntegerField(default=0)
    session_duration = models.IntegerField(choices=SessionDuration)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.IntegerField(
        choices=list(CourseStatus.choices),
        default=CourseStatus.DRAFT,
    )
    responsible_user = None
    owner_user = None

    def __str__(self):
        return self.name
