from django.urls import path
from .admin_views import AdminPaymentListView

urlpatterns = [
    path("payments/", AdminPaymentListView.as_view(), name="admin-payments-list"),
]
