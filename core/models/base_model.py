from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils import timezone

from core.enums import State, Status

AUTH_USER = settings.AUTH_USER_MODEL


class BaseModel(models.Model):
    STATUS_CHOICES = Status
    ACTIVE_STATUSES = {Status.ACTIVE}
    INACTIVE_STATUSES = {Status.INACTIVE}
    DELETED_ACTIVE_STATUSES = {Status.DELETED}
    ALLOWED_STATUSES = {
        State.ACTIVE: ACTIVE_STATUSES,
        State.INACTIVE: INACTIVE_STATUSES,
        State.DELETED: DELETED_ACTIVE_STATUSES,
    }

    state = models.IntegerField(
        choices=list(State.choices),
        default=State.ACTIVE,
    )
    status = models.IntegerField(
        choices=list(Status.choices),
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner_user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.RESTRICT,
        related_name="ownered_%(class)ss",
    )
    responsible_user = models.ForeignKey(
        AUTH_USER,
        on_delete=models.RESTRICT,
        related_name="responsibled_%(class)ss",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        AUTH_USER,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="created_%(class)ss",
    )
    updated_by = models.ForeignKey(
        AUTH_USER,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="updated_%(class)ss",
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.status not in self.STATUS_CHOICES.values:
            raise ValidationError(f"{self.status} is not a valid status!")

        allowed = self.ALLOWED_STATUSES.get(self.state, set())

        if self.status not in allowed:
            raise ValidationError(
                f"{self.status} is not allowed when state is {self.state}!"
            )
