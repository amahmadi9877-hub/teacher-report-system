from django.contrib.contenttypes.models import ContentType

from audits.enums import Action
from audits.models import AuditLog


class AuditService:
    @staticmethod
    def audit_log(*, user, old_obj, new_obj):
        content_type = ContentType.objects.get_for_model(new_obj)
        object_id = str(new_obj.pk)

        if old_obj is not None:
            changes = {}

            for field in old_obj._meta.fields:
                if field.name in {
                    "updated_at",
                    "updated_by",
                }:
                    continue
                old_value = getattr(old_obj, field.name)
                new_value = getattr(new_obj, field.name)

                if old_value != new_value:
                    changes[field.name] = {
                        "old": old_value,
                        "new": new_value,
                    }

            if not changes:
                return

            for field_name, field_value in changes.items():
                AuditLog.objects.create(
                    content_type=content_type,
                    object_id=object_id,
                    field=field_name,
                    action=Action.UPDATE,
                    old_value=str(field_value["old"]),
                    new_value=str(field_value["new"]),
                    changed_by=user,
                )

        else:
            AuditLog.objects.create(
                content_type=content_type,
                object_id=object_id,
                field="__all__",
                action=Action.CREATE,
                old_value=None,
                new_value="created",
                changed_by=user,
            )
