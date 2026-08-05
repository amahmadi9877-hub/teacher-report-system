from django.db import models


class Status(models.IntegerChoices):
    DELETED = -1, "Deleted"
    INACTIVE = 0, "Inactive"
    ACTIVE = 1, "Active"
