from rest_framework.serializers import ValidationError


def PosetiveIntValidator(number: int, number_title: str):
    if not type(number) is int:
        raise ValueError(f"Invalid data type: {type(number)}")
    if number < 0:
        raise ValueError({f"{number_title}": f"{number_title} is not posetive"})
