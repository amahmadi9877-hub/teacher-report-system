from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_role"] = self.user.role
        return data
