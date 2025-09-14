from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.utils.models import TimestampModel

User = settings.AUTH_USER_MODEL


class Cart(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")

    def __str__(self):
        return f"{self.user}의 장바구니"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_products")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])  # 기본값 & 최솟값 1로 지정

    class Meta:
        # unique_together = ("cart", "product")  # 같은 장바구니에 동일 상품 중복 방지
        constraints = [models.UniqueConstraint(fields=["cart", "product"], name="unique_cart_product")]

    def __str__(self):
        return f"{self.cart.user} - {self.product} x {self.quantity}"
