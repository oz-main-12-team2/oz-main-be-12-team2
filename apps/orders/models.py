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
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    recipient_name = models.CharField(max_length=10, blank=False)
    recipient_phone = models.CharField(max_length=20, blank=False)
    recipient_address = models.TextField(blank=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="결제 완료"
    )

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = get_random_string(length=12, allowed_chars="0123456789")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
