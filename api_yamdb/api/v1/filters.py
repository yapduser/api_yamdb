import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для произведений."""

    genre = django_filters.CharFilter(
        field_name="genre__slug",
        lookup_expr="iexact",
    )
    category = django_filters.CharFilter(
        field_name="category__slug",
        lookup_expr="iexact",
    )
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="iexact",
    )
    year = django_filters.NumberFilter(
        field_name="year",
        lookup_expr="iexact",
    )

    class Meta:
        model = Title
        fields = ("category", "genre", "name", "year")
