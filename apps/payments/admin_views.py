from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from .models import Payment
from .serializers import PaymentSerializer


# ✅ 관리자 전용 결제 내역 전체 조회
class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
