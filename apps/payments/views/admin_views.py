from rest_framework import generics, permissions

from apps.core.pagination import CustomPagination

from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer


# ✅ 전체 결제 내역 조회 (관리자 전용)
class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by("-created_at")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination


# ✅ 특정 결제 내역 상세 조회 (관리자 전용)
class AdminPaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]
