from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.enums import State, Status

AUTH_USER = settings.AUTH_USER_MODEL


class BaseModel(models.Model):
    @classmethod
    def make_allowed_statuses(cls):
        return {
            State.ACTIVE: cls.ACTIVE_STATUSES,
            State.INACTIVE: cls.INACTIVE_STATUSES,
            State.DELETED: cls.DELETED_ACTIVE_STATUSES,
        }

    STATUS_CHOICES = Status
    DEFAULT_ACTIVE_STATUS = Status.ACTIVE
    ACTIVE_STATUSES = {Status.ACTIVE}
    INACTIVE_STATUSES = {Status.INACTIVE}
    DELETED_ACTIVE_STATUSES = {Status.DELETED}

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
        null=True,
        blank=True,
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

        if self.status not in self.make_allowed_statuses().get(self.state, set()):
            raise ValidationError(
                {
                    "__all__": f"The selected status '{self.status}' is not valid for the current state '{self.state}'!"
                }
            )
