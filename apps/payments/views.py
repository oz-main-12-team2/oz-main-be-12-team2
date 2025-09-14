from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from .models import Payment
from .serializers import PaymentSerializer


# ✅ 결제 내역 전체 조회 & 생성
class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# ✅ 단일 결제 상세 조회 & 수정 & 삭제
class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
