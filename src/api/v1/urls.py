from django.urls import path

from api.v1.views import (
    CertificateListView,
    CertificateOrderProcessingView,
    PaymentStatusView,
    YookassaReturnUrlView,
)


urlpatterns = [
    path("certificates/", CertificateListView.as_view(), name="certificates"),
    path(
        "certificate-order/create/",
        CertificateOrderProcessingView.as_view(),
        name="create_certificate_order",
    ),
    path("return-url/", YookassaReturnUrlView.as_view(), name="return_url"),
    path(
        "changed-payment-status/",
        PaymentStatusView.as_view(),
        name="payment_status",
    ),
]
