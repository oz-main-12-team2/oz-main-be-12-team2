from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication

from .models import Payment
from .serializers import PaymentSerializer


# ✅ 전체 결제 내역 조회 (관리자 전용)
class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by("-created_at")
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]


# ✅ 특정 결제 내역 상세 조회 (관리자 전용)
class AdminPaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
