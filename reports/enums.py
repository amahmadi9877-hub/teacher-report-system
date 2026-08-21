from django.db import models


class ReportStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    WAITING_FOR_REVIEW = 1, "Waiting_for_review"
    APPROVED = 2, "Approved"
    REJECTED = 3, "Rejected"
    DELETED = -1, "Deleted"
