from django.db import models

from apps.utils.models import TimestampModel


class Product(TimestampModel):
    name = models.CharField(max_length=255, verbose_name="상품명")
    description = models.TextField(verbose_name="상품 상세 설명", blank=True)
    author = models.CharField(max_length=100, verbose_name="작가", default="작자 미상")
    publisher = models.CharField(max_length=100, verbose_name="출판사", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="가격")
    stock = models.IntegerField(verbose_name="재고 수량")
    category = models.CharField(max_length=20, verbose_name="카테고리", blank=True, null=True)
    image = models.ImageField(upload_to="", verbose_name="책 이미지", blank=True, null=True)

    def __str__(self):
        """객체를 문자열로 표현할 때 사용"""
        return self.name

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품 목록"
        ordering = ["-created_at"]  # 최신 상품이 먼저 보이도록 정렬
