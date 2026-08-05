from django.db import models


class ReportStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    WAITING_FOR_EDIT = 1, "Waiting_for_edit"
    WAITING_FOR_REVIEW = 2, "Waiting_for_review"
    APPROVED = 3, "Approved"
    REJECTED = 4, "Rejected"
    DELETED = -1, "Deleted"
