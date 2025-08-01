import logging
import os

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import get_client_ip
from api.v1.serializers import (
    CertificateListSerializer,
    CertificateOrderCreateSerializer,
    CertificateOrderInfoSerializer,
    YookassaNotificationSerializer,
)
from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
    UnexpectedYokassaNotificationStatus,
)
from orders.models import Certificate
from orders.services import (
    get_certificate_order_info,
    process_certificate_order,
    process_yookassa_notification,
)


logger = logging.getLogger(__name__)


class CertificateListView(ListAPIView):
    """Получить все доступные для продажи сертификаты."""

    queryset = Certificate.objects.filter(is_active=True)
    serializer_class = CertificateListSerializer


@extend_schema(
    request=CertificateOrderCreateSerializer,
    responses={
        200: OpenApiResponse(description="URL для оплаты"),
        404: OpenApiResponse(description="Сертификат не найден"),
    },
)
class CertificateOrderProcessingView(APIView):
    """
    Предварительное создание заказа сертификата (со статусом "В процессе").
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


@extend_schema(exclude=True)
class PaymentStatusView(APIView):
    """
    Обрабатывает уведомления о смене статуса платежа, полученные от ЮКассы.

    API ЮКассы требует в ответ на уведомления только код 200.
    Документация говорит:
    "Вам нужно подтвердить, что вы получили уведомление.
    Для этого ответьте кодом состояния HTTP 200. ЮKassa проигнорирует всё,
    что будет находиться в теле или заголовках ответа. Ответы с любыми другими
    кодами состояний HTTP будут считаться невалидными, и ЮKassa продолжит
    доставлять уведомление в течение 24 часов, начиная с момента,
    когда событие произошло."
    https://yookassa.ru/developers/using-api/webhooks#using
    """

    def post(self, request) -> Response:
        ip = get_client_ip(request)
        if ip in os.getenv("YOOKASSA_NOTIFICATION_IPS", ""):
            serializer = YookassaNotificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                process_yookassa_notification(serializer.validated_data)
                return Response(status=status.HTTP_200_OK)
            except UnexpectedYokassaNotificationStatus:
                raise ParseError("Unexpected Yookassa notification status.")
            except CertificateOrderNotFoundError:
                raise NotFound("Заказ не найден!")
        else:
            logger.warning("Got the wrong IP: %s. It's not from Yookassa.", ip)
            raise ParseError("Wrong client IP. Bad Request.")


@extend_schema(
    responses={
        200: CertificateOrderInfoSerializer,
        404: OpenApiResponse(description="Заказ не найден"),
    },
)
class CertificateOrderUseView(APIView):
    """
    Использование сертификата.
    При GET-запросе — выдает данные заказа, ожидает списание.
    При POST-запросе — списывает заказ (CertificateOrder.is_used = True).
    """

    def get(self, request, *args, **kwargs) -> Response:
        try:
            order_info = get_certificate_order_info(self.kwargs.get("id"))
            serializer = CertificateOrderInfoSerializer(order_info)
            return Response(serializer.data)
        except CertificateOrderNotFoundError:
            raise NotFound("Заказ не найден!")

    # def post(self, request, id: UUID) -> Response:
    #     pass
