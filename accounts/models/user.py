from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from accounts.enums import UserRole

# Create your models here.


class User(AbstractUser):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    backup_phone_number = models.CharField(
        max_length=14,
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
    )
    REQUIRED_FIELDS = ["first_name", "last_name", "role", "phone_number"]

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        super().clean()

        if self.role == UserRole.TEACHER and not self.backup_phone_number:
            raise ValidationError(
                {"backup_phone_number": "Backup phone number is required for teachers!"}
            )
