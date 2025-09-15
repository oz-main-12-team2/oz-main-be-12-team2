from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "display_price"]
    fields = ["product", "quantity", "display_price"]  # admin에 보여줄 순서

    def display_price(self, obj):
        return obj.price

    display_price.short_description = "Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "recipient_name", "recipient_phone", "recipient_address", "created_at"]
    inlines = [OrderItemInline]
