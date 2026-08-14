from rest_framework import serializers
from accounts.serializers import UserModelSerializer


class BaseModelSerializer(serializers.ModelSerializer):
    created_by = UserModelSerializer(read_only=True)
    updated_by = UserModelSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    state = serializers.IntegerField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    owner_user = UserModelSerializer(read_only=True)
    responsible_user = UserModelSerializer(read_only=True)

    def validate(self, attrs):

        model = self.Meta.model

        status = attrs.get("status", getattr(self.instance, "status", None))

        state = attrs.get("state", getattr(self.instance, "state", None))

        if state == None and status == None:
            return attrs

        if status not in model.STATUS_CHOICES.values:
            raise serializers.ValidationError({"status": f"{status} is not valid."})

        if status not in model.make_allowed_statuses().get(state, set()):
            raise serializers.ValidationError(
                {"__all__": f"Status {status} is not allowed for state {state}."}
            )

        return attrs
