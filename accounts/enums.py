from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "Admin", "admin"
    TEACHER = "teacher", "Teacher"
    EDUCATION_OFFICER = "education officer", "Education Officer"
    FINANCE_OFFICER = "finance officer", "Finance Officer"
