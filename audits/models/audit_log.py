from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey

from audits.enums import Action


class AuditLog(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    object_id = models.CharField(max_length=100)

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    field = models.CharField(max_length=100)

    action = models.IntegerField(choices=Action)

    old_value = models.TextField(
        null=True,
        blank=True,
    )

    new_value = models.TextField(
        null=True,
        blank=True,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
