from rest_framework import serializers


class BulkDeactivateSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    status = serializers.IntegerField()
