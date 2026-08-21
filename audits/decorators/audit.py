from functools import wraps
from audits.services import AuditService


def audit(func):
    @wraps(func)
    def wrapper(self, serializer, *args, **kwargs):
        old_obj = None
        if serializer.instance:
            old_obj = serializer.instance.__class__.objects.get(
                pk=serializer.instance.pk
            )

        result = func(self, serializer, *args, **kwargs)

        new_obj = serializer.instance.__class__.objects.get(pk=serializer.instance.pk)

        AuditService.audit_log(
            user=self.request.user,
            old_obj=old_obj,
            new_obj=new_obj,
        )

        return result

    return wrapper
