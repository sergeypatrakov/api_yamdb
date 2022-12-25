from django_filters import BaseInFilter, CharFilter, FilterSet

from reviews.models import Title


class SlugFilterInFilter(BaseInFilter, CharFilter):
    pass


class GenreFilter(FilterSet):
    genre = SlugFilterInFilter(field_name='genre__slug', lookup_expr='in')
    category = SlugFilterInFilter(
        field_name='category__slug',
        lookup_expr='in'
    )

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
