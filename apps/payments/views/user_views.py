from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer


# ✅ 결제 내역 생성
class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.user != self.request.user:
            raise PermissionDenied("본인 주문에 대해서만 결제할 수 있습니다.")
        serializer.save()


# ✅ 본인 결제 내역 조회 (리스트)
class UserPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).order_by("-created_at")


# ✅ 본인 결제 상세 조회
class UserPaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)
