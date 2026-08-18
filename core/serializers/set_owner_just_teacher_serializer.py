from django.contrib.auth import get_user_model
from rest_framework import serializers

AUTH_USER = get_user_model()


class SetOwnerJustTeacherSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=AUTH_USER.objects.filter(role="teacher")
    )
