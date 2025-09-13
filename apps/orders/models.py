from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    """
    상품 정보를 담는 모델입니다.
    """
    name = models.CharField(max_length=255, verbose_name="상품명")
    description = models.TextField(verbose_name="상품 상세 설명", blank=True)
    author = models.CharField(max_length=100, verbose_name="작가", default="작자 미상")
    publisher = models.CharField(
        max_length=100, verbose_name="출판사", blank=True, null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="가격")
    stock = models.IntegerField(verbose_name="재고 수량")
    category = models.CharField(
        max_length=20, verbose_name="카테고리", blank=True, null=True
    )
    image_url = models.CharField(
        max_length=255, verbose_name="책 이미지 url", default="기본이미지url"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품 목록"
        ordering = ["-created_at"]



class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE) #이부분수정 외래키연결을위해
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"



class Cart(models.Model):
    '''
    테스트용 임시 카트
    '''
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"


class CartItem(models.Model):
    '''
    테스트용 임시 카트아이템
    '''
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_item'