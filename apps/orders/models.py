from django.db import models
from django.contrib.auth.models import User

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
    """
    주문 정보를 담는 모델입니다.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="주문자")
    status = models.CharField(max_length=50, default="주문완료", verbose_name="주문 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="주문일")

    def __str__(self):
        return f"주문 #{self.id} ({self.user.username})"

class OrderItem(models.Model):
    """
    주문에 포함된 개별 상품 정보를 담는 모델입니다.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="주문", related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="상품")
    quantity = models.IntegerField(default=1, verbose_name="수량")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="가격")
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity}개) - 주문 #{self.order.id}"