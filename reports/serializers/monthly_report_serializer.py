from rest_framework import serializers


class MonthlyReportCountsSerializer(serializers.Serializer):
    draft = serializers.IntegerField()
    submitted = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
