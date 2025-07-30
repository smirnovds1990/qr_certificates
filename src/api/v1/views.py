from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers import (
    CertificateListSerializer,
    CertificateOrderCreateSerializer,
)
from orders.exceptions import CertificateNotFoundError
from orders.models import Certificate
from orders.services import process_certificate_order


class CertificateListView(ListAPIView):
    """Получить все доступные для продажи сертификаты."""

    queryset = Certificate.objects.filter(is_active=True)
    serializer_class = CertificateListSerializer


@extend_schema(
    request=CertificateOrderCreateSerializer,
    responses={200: OpenApiResponse(description="URL для оплаты")},
)
class CertificateOrderProcessingView(APIView):
    """
    Обработка заказа сертификата.
    Входные данные:
        data = {
            "id": id сертификата,
            "email": почта для отправки сертификата
        }
    Возвращает URL ЮКассы для оплаты.
    """

    def post(self, request) -> Response:
        serializer = CertificateOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            confirmation_url = process_certificate_order(
                serializer.validated_data
            )
            return Response({"confirmation_url": confirmation_url})
        except CertificateNotFoundError:
            raise NotFound("Сертификат не найден.")


@extend_schema(
    responses={
        200: OpenApiResponse(description="Сообщение пользователю после оплаты")
    }
)
class YookassaReturnUrlView(APIView):
    """Представление для редиректа с API ЮКассы после оплаты."""

    def get(self, request) -> Response:
        return Response(
            {
                "message": (
                    "Спасибо за ваш заказ. "
                    "Сертификат будет отправлен на указанный email."
                )
            }
        )
