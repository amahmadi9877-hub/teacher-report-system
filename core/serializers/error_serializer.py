from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    status_code = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    message = serializers.ReadOnlyField()
