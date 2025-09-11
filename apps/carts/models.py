from django.db import models
from django.conf import settings

# User 모델 (settings.AUTH_USER_MODEL 참조)
User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="carts")
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")  # 동일 유저-상품 중복 방지

    def __str__(self):
        return f"{self.user} - {self.product} x {self.quantity}"
