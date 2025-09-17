from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"  # 반드시 전체 경로로 지정
    label = "orders"  # 여기를 추가해서 명시적으로 라벨 지정
