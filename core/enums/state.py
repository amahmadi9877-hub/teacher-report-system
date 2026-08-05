from django.db import models


class State(models.IntegerChoices):
    DELETED = -1, "Deleted"
    INACTIVE = 0, "Inactive"
    ACTIVE = 1, "Active"
