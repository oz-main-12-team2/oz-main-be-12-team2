from django.contrib import admin
from .models import Order  # OrderItem은 아직 코드 없으므로 제거

# OrderItemInline도 제거하거나 주석 처리
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "created_at"]
    # inlines = [OrderItemInline]  # 아직 OrderItem 없으므로 주석 처리.
