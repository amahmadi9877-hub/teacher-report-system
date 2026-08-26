from rest_framework import serializers

from core.enums import Month


class YearAndMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.ChoiceField(choices=Month.choices)
