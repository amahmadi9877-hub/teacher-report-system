from django.db import models

from core.enums import Month
from core.models import BaseModel
from payrolls.enums import PayrollStatus


# Create your models here.
class Payroll(BaseModel):
    STATUS_CHOICES = PayrollStatus
    DEFAULT_ACTIVE_STATUS = {PayrollStatus.DRAFT}
    ACTIVE_STATUSES = {PayrollStatus.DRAFT}
    INACTIVE_STATUSES = {
        PayrollStatus.CALCULATED,
        PayrollStatus.BANED,
        PayrollStatus.NO_SESSION,
    }
    DELETED_STATUSES = {PayrollStatus.DELETED}
    name = models.CharField(max_length=250)
    year = models.IntegerField()
    month = models.IntegerField(choices=Month.choices)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.IntegerField(
        choices=list(PayrollStatus.choices),
        default=PayrollStatus.DRAFT,
    )
    responsible_user = None

    def __str__(self):
        return self.name
