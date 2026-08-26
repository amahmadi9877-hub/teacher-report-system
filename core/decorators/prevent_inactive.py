from rest_framework.exceptions import PermissionDenied
from functools import wraps
from core.enums import State


def prevent_inactive(func):
    @wraps(func)
    def wrapper(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        assert hasattr(obj, "state"), "The object has no 'state' field!"
        if obj.state == State.INACTIVE:
            raise PermissionDenied({"__all__": "Object is deactive and read_only!"})
        return func(self, request, pk, *args, **kwargs)

    return wrapper
