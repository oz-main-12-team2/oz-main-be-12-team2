# apps/stats/views.py
from datetime import datetime

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.stats import services
from apps.stats.serializers import DashboardSerializer


class DashboardAPIView(GenericAPIView):
    """
    관리자 대시보드 통계 조회
    GET /api/admin/stats/dashboard
    """

    permission_classes = [IsAdminUser]
    serializer_class = DashboardSerializer
    pagination_class = None
    filter_backends = []

    def get(self, request, *args, **kwargs):
        base_date = datetime.today().date()
        data = services.get_dashboard_data(base_date)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
