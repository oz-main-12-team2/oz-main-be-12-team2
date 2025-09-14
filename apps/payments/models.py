from django.db import models


class PaymentMethod(models.TextChoices):
    CARD = "CARD", "신용카드"
    BANK = "BANK", "계좌이체"
    KAKAO = "KAKAO", "카카오페이"
    NAVER = "NAVER", "네이버페이"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "결제 대기"
    SUCCESS = "SUCCESS", "결제 성공"
    FAILED = "FAILED", "결제 실패"
    REFUNDED = "REFUNDED", "환불"


class Payment(models.Model):
    order = models.ForeignKey("apps.orders.Order", on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
