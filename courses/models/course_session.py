from django.db import models

from core.models import BaseModel
from courses.enums import CourseSessionStatus


# Create your models here.
class CourseSession(BaseModel):
    STATUS_CHOICES = CourseSessionStatus
    ACTIVE_STATUSES = {CourseSessionStatus.DRAFT, CourseSessionStatus.IN_PROGRESS}
    INACTIVE_STATUSES = {CourseSessionStatus.COMPLETED, CourseSessionStatus.CANCELED}
    DELETED_ACTIVE_STATUSES = {CourseSessionStatus.DELETED}
    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    course = models.ForeignKey("courses.Course", on_delete=models.RESTRICT)
    course_schedul = models.ForeignKey(
        "courses.CourseSchedule", on_delete=models.SET_NULL, blank=True, null=True
    )
    status = models.IntegerField(
        choices=list(CourseSessionStatus.choices),
        default=CourseSessionStatus.DRAFT,
    )

    def __str__(self):
        return self.name
