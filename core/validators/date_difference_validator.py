from datetime import timedelta
from rest_framework.serializers import ValidationError


ALLOWED_SCOPES = {
    "weeks",
    "days",
}


def DateDifferenceValidator(
    date1,
    date2,
    date1_label="date1",
    date2_label="date2",
    scope="days",
    minimum_difference=0,
    exact=False,
):
    if scope not in ALLOWED_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")
    if exact:
        if date2 - date1 != timedelta(**{scope: minimum_difference}):
            raise ValidationError(
                f"{date2_label} must be exactly {minimum_difference} {scope} after {date1_label}!"
            )
    else:
        if date2 - date1 < timedelta(**{scope: minimum_difference}):
            raise ValidationError(
                f"{date2_label} must be at least {minimum_difference} {scope} after {date1_label}!"
            )
