from rest_framework import serializers


class DeactivateSerializer(serializers.Serializer):
    status = serializers.IntegerField()

    def validate(self, attrs):

        status = attrs.get("status")

        if status not in self.instance.STATUS_CHOICES.values:
            raise serializers.ValidationError({"status": f"{status} is not valid."})

        if status not in self.instance.make_allowed_statuses().get(0, set()):
            raise serializers.ValidationError(
                {"status": f"Status {status} is not allowed for state 0."}
            )

        return attrs
