from rest_framework import serializers
from core.serializers import DeactivateSerializer


class SessionReportDeactivateSerializer(DeactivateSerializer):
    reviewer_description = serializers.CharField()
