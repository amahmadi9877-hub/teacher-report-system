from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    response.data = {
        "status_code": response.status_code,
        "code": getattr(exc, "default_code", "error"),
        "message": response.data,
    }

    return response
