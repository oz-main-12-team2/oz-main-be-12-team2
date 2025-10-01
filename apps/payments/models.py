from django.db import models


class PaymentMethod(models.TextChoices):
    CARD = "카드", "카드"  # value, label
    BANK = "계좌이체", "계좌이체"
    PHONE = "휴대폰 결제", "휴대폰 결제"


class PaymentStatus(models.TextChoices):
    PENDING = "대기", "대기"  # 실제 결제 서비스 구현시 사용 예정
    SUCCESS = "성공", "성공"
    FAIL = "실패", "실패"
    CANCEL = "취소", "취소"


class Payment(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # 모의결제용 트랜잭션 ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.id}] {self.method} - {self.total_price} ({self.status})"
