from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin"
    TEACHER = "teacher"
    EDUCATION_OFFICER = "education_officer"
    FINANCE_OFFICER = "finance_officer"

    @classmethod
    def selectable_choices(cls):
        return [role.value for role in cls if role != cls.ADMIN]
