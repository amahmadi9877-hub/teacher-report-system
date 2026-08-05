from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "code": "validation_error",
                "errors": (
                    exc.message_dict
                    if hasattr(exc, "message_dict")
                    else {"detail": exc.messages}
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = exception_handler(exc, context)

    if response is None:
        return None

    response.data = {
        "status_code": response.status_code,
        "code": getattr(exc, "default_code", "error"),
        "errors": response.data,
    }

    return response
