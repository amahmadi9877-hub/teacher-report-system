from django.db import models

from core.models import BaseModel
from courses.enums import AcademicTermStatus


# Create your models here.
class AcademicTerm(BaseModel):
    STATUS_CHOICES = AcademicTermStatus
    ACTIVE_STATUSES = {AcademicTermStatus.DRAFT, AcademicTermStatus.IN_PROGRESS}
    INACTIVE_STATUSES = {AcademicTermStatus.COMPLETED, AcademicTermStatus.CANCELED}
    DELETED_ACTIVE_STATUSES = {AcademicTermStatus.DELETED}
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.IntegerField(
        choices=list(AcademicTermStatus.choices),
        default=AcademicTermStatus.DRAFT,
    )

    def __str__(self):
        return self.name
