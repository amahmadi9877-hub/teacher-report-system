from rest_framework.serializers import ValidationError


def posetive_decimal_validator(number, number_title: str):
    if number < 0:
        raise ValidationError({f"{number_title}": f"{number_title} is not posetive"})
