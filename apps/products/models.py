# apps/products/models.py
from django.db import models


class Product(models.Model):
    """
    상품 정보를 담는 모델입니다.
    """

    # id 필드는 장고가 자동으로 Primary Key로 생성합니다.

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

    # auto_now_add: 객체 최초 생성 시 현재 시간으로 자동 저장
    # auto_now: 객체가 수정될 때마다 현재 시간으로 자동 업데이트
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        """객체를 문자열로 표현할 때 사용"""
        return self.name

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품 목록"
        ordering = ["-created_at"]  # 최신 상품이 먼저 보이도록 정렬