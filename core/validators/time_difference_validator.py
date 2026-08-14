from datetime import time
from rest_framework.serializers import ValidationError


ALLOWED_SCOPES = {
    "hours",
    "minutes",
}


def TimeDifferenceValidator(
    time1: time,
    time2: time,
    time1_label="time1",
    time2_label="time2",
    scope="minutes",
    minimum_difference=0,
    exact=False,
):
    if scope not in ALLOWED_SCOPES:
        raise ValueError(f"Invalid scope: {scope}")

    time1_minutes = time1.hour * 60 + time1.minute
    time2_minutes = time2.hour * 60 + time2.minute

    difference = time2_minutes - time1_minutes

    if scope == "hours":
        expected_difference = minimum_difference * 60
    else:
        expected_difference = minimum_difference

    if exact:
        if difference != expected_difference:
            raise ValidationError(
                f"{time2_label} must be exactly {minimum_difference} {scope} after {time1_label}!"
            )
    elif difference < expected_difference:
        raise ValidationError(
            f"{time2_label} must be at least {minimum_difference} {scope} after {time1_label}!"
        )
