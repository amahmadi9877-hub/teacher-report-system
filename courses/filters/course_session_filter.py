import django_filters

from courses.models import CourseSession


class CourseSessionFilter(django_filters.FilterSet):
    school = django_filters.NumberFilter(
        field_name="course__school_id",
    )

    course = django_filters.NumberFilter(
        field_name="course_id",
    )

    term = django_filters.NumberFilter(
        field_name="course__academic_term_id",
    )
    teacher = django_filters.NumberFilter(
        field_name="owner_user_id",
    )

    date_after = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )

    date_before = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
    )

    class Meta:
        model = CourseSession
        fields = [
            "school",
            "course",
            "term",
            "teacher",
            "date_after",
            "date_before",
        ]
