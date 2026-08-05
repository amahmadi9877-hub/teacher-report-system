from django.db import models

from core.models import BaseModel


# Create your models here.
class CourseInstructor(BaseModel):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
