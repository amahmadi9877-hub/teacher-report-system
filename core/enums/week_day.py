from django.db import models


class WeekDay(models.IntegerChoices):
    MONDAY = 1, "Mon"
    TUESDAY = 2, "Tue"
    WEDNESDAY = 3, "Wed"
    THURSDAY = 4, "Thu"
    FRIDAY = 5, "Fri"
    SATURDAY = 6, "Sat"
    SUNDAY = 7, "Sun"
