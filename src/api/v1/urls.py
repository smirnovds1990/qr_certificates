from django.urls import path

from api.v1.views import (
    CertificateListView,
    CertificateOrderProcessingView,
    CertificateOrderUseView,
    GenerateQRView,
    PaymentStatusView,
    ResendOrderView,
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
    path(
        "certificate-order/<uuid:id>/",
        CertificateOrderUseView.as_view(),
        name="use_certificate",
    ),
    path(
        "certificate-order/resend/",
        ResendOrderView.as_view(),
        name="resend_certificate_order",
    ),
    path(
        "generate-qrcode/<uuid:id>/",
        GenerateQRView.as_view(),
        name="generate_qrcode",
    ),
]
