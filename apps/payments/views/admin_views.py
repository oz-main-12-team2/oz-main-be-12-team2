from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import CustomPagination
from apps.payments.filters import PaymentFilter
from apps.payments.mock_payment.payment import cancel_payment
from apps.payments.models import Payment, PaymentStatus
from apps.payments.serializers import AdminPaymentSerializer


# ✅ 전체 결제 내역 조회 (관리자 전용)
class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by("-created_at")
    serializer_class = AdminPaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination

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
        """관리자 결제 내역 조회 (상태 + 기간 필터링 가능)"""
        return super().get(request, *args, **kwargs)


# ✅ 특정 결제 내역 상세 조회 (관리자 전용)
class AdminPaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = AdminPaymentSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPaymentCancelView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        payment = Payment.objects.filter(pk=pk).first()
        if not payment:
            return Response({"detail": "결제 내역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        result = cancel_payment(payment.transaction_id)

        # ✅ 실패한 결제 취소
        if result["status"] == PaymentStatus.FAIL.value and "취소할 수 없습니다" in result["message"]:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 이미 취소된 결제
        if result["status"] == PaymentStatus.CANCEL.value and "이미 취소된" in result["message"]:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        payment.status = result["status"]
        payment.save()

        return Response(result, status=status.HTTP_200_OK)
