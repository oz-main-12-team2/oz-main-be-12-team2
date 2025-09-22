from django.db import models

from apps.users.models import User


class Inquiry(models.Model):
    CATEGORY_CHOICES = [
        ("order", "주문 관련"),
        ("shipping", "배송 문의"),
        ("product", "상품 문의"),
        ("payment", "결제/환불"),
        ("account", "회원 정보"),
        ("other", "기타"),
    ]

    STATUS_CHOICES = [
        ("submitted", "접수"),
        ("in_progress", "처리중"),
        ("completed", "완료"),
        ("on_hold", "보류"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquiries")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class InquiryReply(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 수정
    content = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        author_name = self.author.email if self.author else "상담원 제미나이"
        return f"{self.inquiry.title} 답변 - {author_name}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ("order", "주문 관련"),
        ("shipping", "배송 문의"),
        ("product", "상품 문의"),
        ("payment", "결제/환불"),
        ("account", "회원 정보"),
        ("other", "기타"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.CharField(max_length=200)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.question
