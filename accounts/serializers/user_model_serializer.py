from rest_framework import serializers

from accounts.models import User


class LowDetailUserModelSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class HighDetailUserModelSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "phone_number", "backup_phone_number"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
