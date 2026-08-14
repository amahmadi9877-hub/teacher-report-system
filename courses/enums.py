from django.db import models


class AcademicTermStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    IN_PROGRESS = 1, "In Progress"
    COMPLETED = 2, "Completed"
    CANCELED = 3, "Canceled"
    DELETED = -1, "Deleted"


class CourseStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    SCHEDULING = 1, "Scheduling"
    SCHEDULED = 2, "Scheduled"
    IN_PROGRESS = 3, "In Progress"
    COMPLETED = 4, "Completed"
    CANCELED = 5, "Canceled"
    DELETED = -1, "Deleted"


class CourseSessionStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    IN_PROGRESS = 1, "In Progress"
    COMPLETED = 2, "Completed"
    CANCELED = 3, "Canceled"
    DELETED = -1, "Deleted"


class SessionDuration(models.IntegerChoices):
    MINUTES_60 = 60, "60 minutes"
    MINUTES_90 = 90, "90 minutes"
    MINUTES_120 = 120, "120 minutes"
