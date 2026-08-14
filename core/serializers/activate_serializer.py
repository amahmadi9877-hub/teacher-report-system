from rest_framework import serializers


class ActivateSerializer(serializers.Serializer):
    status = serializers.IntegerField()

    def validate(self, attrs):

        status = attrs.get("status")

        if status not in self.instance.STATUS_CHOICES.values:
            raise serializers.ValidationError({"status": f"{status} is not valid."})

        if status not in self.instance.make_allowed_statuses().get(1, set()):
            raise serializers.ValidationError(
                {"status": f"Status {status} is not allowed for state 1."}
            )

        return attrs
