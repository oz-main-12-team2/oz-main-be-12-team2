from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.filters import PaymentFilter
from apps.payments.mock_payment.payment import cancel_payment, process_payment
from apps.payments.models import Payment, PaymentStatus
from apps.payments.serializers import PaymentSerializer


# ✅ 결제 내역 생성
class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]

        if order.user != self.request.user:
            raise PermissionDenied("본인 주문에 대해서만 결제할 수 있습니다.")

        # ✅ 이미 성공한 결제 내역이 있는지 확인
        if order.payments.filter(status=PaymentStatus.SUCCESS.value).exists():
            raise ParseError("이미 결제가 완료된 주문입니다.")

        # ✅ 결제 요청 (mock_payment)
        result = process_payment(order.total_price, serializer.validated_data["method"])

        serializer.save(
            status=result["status"],
            transaction_id=result["transaction_id"],
        )


# ✅ 본인 결제 내역 조회 (리스트)
class UserPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    # ✅ Swagger 수동 파라미터 등록
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="결제 상태 (대기, 성공, 실패, 취소)",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Payment._meta.get_field("status").choices],
            ),
            openapi.Parameter(
                "created_at__gte",
                openapi.IN_QUERY,
                description="시작일 (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
            openapi.Parameter(
                "created_at__lte",
                openapi.IN_QUERY,
                description="종료일 (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """결제 내역을 상태와 기간으로 필터링"""
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).order_by("-created_at")


# ✅ 본인 결제 상세 조회
class UserPaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


# ✅ 결제 취소 (사용자)
class UserPaymentCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        payment = Payment.objects.filter(pk=pk, order__user=request.user).first()
        if not payment:
            return Response({"detail": "결제 내역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        result = cancel_payment(payment.transaction_id)
        payment.status = result["status"]
        payment.save()

        return Response(result, status=status.HTTP_200_OK)
