from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string

from apps.products.models import Product
from apps.utils.models import TimestampModel


class Order(TimestampModel):
    STATUS_CHOICES = [
        ("결제 완료", "결제 완료"),
        ("배송중", "배송중"),
        ("배송완료", "배송완료"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ 기본값 0
    recipient_name = models.CharField(max_length=10, blank=False)
    recipient_phone = models.CharField(max_length=20, blank=False)
    recipient_address = models.TextField(blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="결제 완료")

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = get_random_string(length=12, allowed_chars="0123456789")
        super().save(*args, **kwargs)

    def update_total_price(self):
        """주문에 속한 모든 OrderItem 기준으로 총합 계산"""
        total = sum(item.total_price for item in self.items.all())
        self.total_price = total
        super().save(update_fields=["total_price"])  # ✅ total_price만 업데이트

    def __str__(self):
        return f"Order {self.order_number} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # ✅ 개별 아이템 total_price 계산
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # ✅ 관련 주문의 total_price 다시 계산
        self.order.update_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # ✅ 아이템 삭제 후에도 주문 금액 재계산
        self.order.update_total_price()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
