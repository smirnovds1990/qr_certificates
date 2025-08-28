from django.urls import path

from api.v1.views import (
    CertificateListView,
    CertificateOrderProcessingView,
    PaymentStatusView,
)


urlpatterns = [
    path("certificates/", CertificateListView.as_view(), name="certificates"),
    path(
        "certificate-order/create/",
        CertificateOrderProcessingView.as_view(),
        name="create_certificate_order",
    ),
    path(
        "changed-payment-status/",
        PaymentStatusView.as_view(),
        name="payment_status",
    ),
]
