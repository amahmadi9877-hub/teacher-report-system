from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"
    EDUCATION_OFFICER = "education_officer", "Education_Officer"
    FINANCE_OFFICER = "finance_officer", "Finance_Officer"

    @classmethod
    def selectable_choices(cls):
        return [role.value for role in cls if role != cls.ADMIN]
