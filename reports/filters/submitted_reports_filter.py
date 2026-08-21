import django_filters

from reports.models import SessionReport


class SubmittedReportsFilter(django_filters.FilterSet):
    school = django_filters.NumberFilter(
        field_name="course_session__course__school_id",
    )

    course = django_filters.NumberFilter(
        field_name="course_session__course_id",
    )

    instructor = django_filters.NumberFilter(
        field_name="owner_user_id",
    )

    date_after = django_filters.DateFilter(
        field_name="course_session__date",
        lookup_expr="gte",
    )

    date_before = django_filters.DateFilter(
        field_name="course_session__date",
        lookup_expr="lte",
    )

    class Meta:
        model = SessionReport
        fields = [
            "school",
            "course",
            "instructor",
            "date_after",
            "date_before",
        ]
