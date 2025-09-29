from django.db import models

from apps.core.models import TimestampModel


class ProductCategory(models.TextChoices):
    NOVEL = "소설", "소설"
    PROGRAMMING = "프로그래밍", "프로그래밍"
    POETRY_ESSAY = "시/에세이", "시/에세이"
    HUMANITIES = "인문", "인문"
    FAMILY_PARENTING = "가정/육아", "가정/육아"
    COOKING = "요리", "요리"
    HEALTH = "건강", "건강"
    HOBBY_SPORTS = "취미/실용/스포츠", "취미/실용/스포츠"
    COMPUTER_IT = "컴퓨터/IT", "컴퓨터/IT"
    ECONOMY_BUSINESS = "경제/경영", "경제/경영"
    SELF_IMPROVEMENT = "자기계발", "자기계발"
    POLITICS_SOCIETY = "정치/사회", "정치/사회"
    HISTORY_CULTURE = "역사/문화", "역사/문화"
    RELIGION = "종교", "종교"
    ART_POPCULTURE = "예술/대중문화", "예술/대중문화"
    STUDY_GUIDE = "중/고등참고서", "중/고등참고서"
    ENGINEERING = "기술/공학", "기술/공학"
    FOREIGN_LANGUAGE = "외국어", "외국어"
    SCIENCE = "과학", "과학"
    JOB_EXAM = "취업/수험서", "취업/수험서"
    TRAVEL = "여행", "여행"


class Product(TimestampModel):
    name = models.CharField(max_length=255, verbose_name="상품명")
    description = models.TextField(verbose_name="상품 상세 설명", blank=True)
    author = models.CharField(max_length=100, verbose_name="작가", default="작자 미상")
    publisher = models.CharField(max_length=100, verbose_name="출판사", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="가격")
    stock = models.IntegerField(verbose_name="재고 수량")
    category = models.CharField(max_length=20, choices=ProductCategory.choices)
    image = models.ImageField(upload_to="", verbose_name="책 이미지", default="products/product_default.jpg")

    def __str__(self):
        """객체를 문자열로 표현할 때 사용"""
        return self.name

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품 목록"
        ordering = ["-created_at"]  # 최신 상품이 먼저 보이도록 정렬
