from django.apps import AppConfig


class CartsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.carts"

    # 앱 로드시 실행되는 코드
    def ready(self):
        import apps.carts.signals  # noqa : F401
