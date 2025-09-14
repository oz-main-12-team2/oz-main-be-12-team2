from django.urls import path

from .admin_views import AdminPaymentDetailView, AdminPaymentListView

urlpatterns = [
    path("", AdminPaymentListView.as_view(), name="admin-payment-list"),
    path("<int:pk>/", AdminPaymentDetailView.as_view(), name="admin-payment-detail"),
]
