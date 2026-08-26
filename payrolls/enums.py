from django.db import models


class PayrollStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    CALCULATED = 1, "Calculated"
    BANED = 2, "Baned"
    NO_SESSION = 3, "No session"
    DELETED = -1, "Deleted"
