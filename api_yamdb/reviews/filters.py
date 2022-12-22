import django_filters

from reviews.models import Title


class SlugFilterInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class GenreFilter(django_filters.FilterSet):
    genre = SlugFilterInFilter(field_name="genre__slug", lookup_expr='in')
    category = SlugFilterInFilter(field_name="category__slug", lookup_expr='in')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
