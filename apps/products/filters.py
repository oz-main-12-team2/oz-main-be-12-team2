import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # 개별 필터
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category", lookup_expr="icontains")

    # 가격 필터
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # 전체 검색
    query = django_filters.CharFilter(method="filter_query")

    class Meta:
        model = Product
        fields = ["name", "description", "author", "category", "min_price", "max_price"]

    def filter_query(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(author__icontains=value)
            | Q(category__icontains=value)
        )
