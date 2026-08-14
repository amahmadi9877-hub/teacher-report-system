from django.db import models


class WeekDay(models.IntegerChoices):
    MONDAY = 0, "Mon"
    TUESDAY = 1, "Tue"
    WEDNESDAY = 2, "Wed"
    THURSDAY = 3, "Thu"
    FRIDAY = 4, "Fri"
    SATURDAY = 5, "Sat"
    SUNDAY = 6, "Sun"
