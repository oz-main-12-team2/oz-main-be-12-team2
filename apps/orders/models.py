import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

from apps.core.models import TimestampModel
from apps.products.models import Product


class Order(TimestampModel):
    STATUS_CHOICES = [
        ("결제 완료", "결제 완료"),
        ("배송중", "배송중"),
        ("배송완료", "배송완료"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recipient_name = models.CharField(max_length=10, blank=False)
    recipient_phone = models.CharField(max_length=20, blank=False)
    recipient_address = models.TextField(blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="결제 완료")

    def clean(self):
        if not (2 <= len(self.recipient_name) <= 10):
            raise ValidationError("수령자 이름은 2~10자여야 합니다.")
        if not re.match(r"^01[016789]-\d{3,4}-\d{4}$", self.recipient_phone):
            raise ValidationError("전화번호 형식이 올바르지 않습니다.")
        if self.total_price < 0:
            raise ValidationError("총 금액은 0 이상이어야 합니다.")
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError("상태 값이 올바르지 않습니다.")
        super().clean()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = get_random_string(length=12, allowed_chars="0123456789")
        self.full_clean()
        super().save(*args, **kwargs)

    def update_total_price(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_price = total
        super().save(update_fields=["total_price"])

    def __str__(self):
        return f"Order {self.order_number} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("수량은 1 이상이어야 합니다.")
        if self.unit_price < 0:
            raise ValidationError("상품 가격은 0 이상이어야 합니다.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.update_total_price()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
