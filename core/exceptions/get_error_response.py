from rest_framework import status
from rest_framework.response import Response

from core.dataclasses import ResponseError
from core.serializers import ErrorSerializer


def get_error_response(
    code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    return Response(
        ErrorSerializer(
            instance=ResponseError(
                status_code=status_code,
                code=code,
                message=message,
            )
        ).data,
        status=status_code,
    )
