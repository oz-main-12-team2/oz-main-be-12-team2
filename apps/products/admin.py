from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "price")
    list_display_links = ("__str__",)  # __str__ 컬럼 클릭 시 상세 페이지로 이동
