from django.db import models

from core.models import BaseModel
from courses.models import AcademicTerm


# Create your models here.
class TeacherPayRate(BaseModel):
    name = models.CharField(max_length=250)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.RESTRICT)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    responsible_user = None

    def __str__(self):
        return self.name
