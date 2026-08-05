from django.db import models

from core.models import BaseModel
from payrolls.enums import PayrollStatus


# Create your models here.
class Payroll(BaseModel):
    STATUS_CHOICES = PayrollStatus
    ACTIVE_STATUSES = {PayrollStatus.DRAFT}
    INACTIVE_STATUSES = {PayrollStatus.CALCULATED, PayrollStatus.BANED}
    DELETED_ACTIVE_STATUSES = {PayrollStatus.DELETED}
    name = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(
        choices=list(PayrollStatus.choices),
        default=PayrollStatus.DRAFT,
    )

    def __str__(self):
        return self.name
