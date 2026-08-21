from django.db import models

from core.models import BaseModel
from courses.enums import AcademicTermStatus


# Create your models here.
class AcademicTerm(BaseModel):
    STATUS_CHOICES = AcademicTermStatus
    DEFAULT_ACTIVE_STATUS = AcademicTermStatus.DRAFT
    ACTIVE_STATUSES = {AcademicTermStatus.DRAFT, AcademicTermStatus.IN_PROGRESS}
    INACTIVE_STATUSES = {AcademicTermStatus.COMPLETED, AcademicTermStatus.CANCELED}
    DELETED_STATUSES = {AcademicTermStatus.DELETED}
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_summer = models.BooleanField(default=False)
    status = models.IntegerField(
        choices=list(AcademicTermStatus.choices),
        default=AcademicTermStatus.DRAFT,
    )
    responsible_user = None
    owner_user = None

    def __str__(self):
        return self.name
