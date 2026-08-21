from django.db import models


class Action(models.IntegerChoices):
    CREATE = 1, "Create"
    UPDATE = 2, "Update"
    DELETED = -1, "Deleted"
