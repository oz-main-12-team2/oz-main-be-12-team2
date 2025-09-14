from django.urls import path
from .admin_views import AdminPaymentListView, AdminPaymentDetailView

urlpatterns = [
    path("payments/", AdminPaymentListView.as_view(), name="admin-payment-list"),
    path("payments/<int:pk>/", AdminPaymentDetailView.as_view(), name="admin-payment-detail"),
]
