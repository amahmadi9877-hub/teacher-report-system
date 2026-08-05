from django.db import models

from core.enums import WeekDay
from core.models import BaseModel


# Create your models here.
class CourseSchedule(BaseModel):
    name = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    week_day = models.IntegerField(choices=WeekDay.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_count = models.IntegerField(default=0)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    course_instructore = models.ForeignKey(
        "courses.CourseInstructor", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name
