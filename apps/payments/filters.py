import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    # 상태 필터
    status = django_filters.ChoiceFilter(choices=Payment._meta.get_field("status").choices)

    # 기간 필터
    created_at__gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte", label="시작일")
    created_at__lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte", label="종료일")

    class Meta:
        model = Payment
        fields = ["status", "created_at"]
