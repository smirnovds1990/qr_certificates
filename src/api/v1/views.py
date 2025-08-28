import logging

# import os
from typing import cast

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status

# from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# from api.utils import get_client_ip
from api.v1.serializers import (
    CertificateListSerializer,
    CertificateOrderCreateSerializer,
    UrlResponseSerializer,
    YookassaNotificationSerializer,
)
from orders.models import Certificate
from orders.services import (
    process_certificate_order,
    process_yookassa_notification,
)
from orders.types import (
    CertificateOrderFormScheme,
    YookassaNotificationScheme,
)


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class CertificateListView(ListAPIView):
    """Получить все доступные для продажи сертификаты."""

    queryset = Certificate.objects.filter(is_active=True)
    serializer_class = CertificateListSerializer


@method_decorator(csrf_exempt, name="dispatch")
@extend_schema(
    request=CertificateOrderCreateSerializer,
    responses={
        200: UrlResponseSerializer,
        404: OpenApiResponse(description="Сертификат не найден"),
        500: OpenApiResponse(description="Ошибка при создании заказа"),
    },
)
class CertificateOrderProcessingView(APIView):
    """
    Предварительное создание заказа сертификата (перед оплатой).
    Создание клиента с данными из формы (если такого клиента еще нет.)
    Входные данные — данные из формы, выбранные/введенные пользователем:
        data = {
            "id": id сертификата,
            "email": почта для отправки сертификата,
            "first_name: имя,
            "last_name: фамилия,
            "phone: телефон,
        }
    Возвращает URL ЮКассы для оплаты.
    """

    def post(self, request) -> Response:
        serializer = CertificateOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_url = process_certificate_order(
            cast(CertificateOrderFormScheme, serializer.validated_data)
        )
        return Response({"confirmation_url": confirmation_url})


@method_decorator(csrf_exempt, name="dispatch")
@extend_schema(
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.INT,
            description="Просто 200 код, как требует API ЮКассы.",
            examples=[OpenApiExample(name="Успешный запрос.", value=200)],
        ),
        400: OpenApiResponse(
            description="Неизвестный статус уведомления от ЮКассы."
        ),
        401: OpenApiResponse(
            description="Неизвестный IP клиента. Это не уведомление от ЮКассы."
        ),
        404: OpenApiResponse(description="Заказ не найден!"),
        500: OpenApiResponse(
            description="Ошибка при отправке письма. Попробуйте позже."
        ),
    }
)
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
        # ip = get_client_ip(request)
        # if ip in os.getenv("YOOKASSA_NOTIFICATION_IPS", ""):
        serializer = YookassaNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        process_yookassa_notification(
            cast(YookassaNotificationScheme, serializer.validated_data)
        )
        return Response(status=status.HTTP_200_OK)
        # else:
        #     logger.warning(
        #         "Got a request from the wrong IP: %s. It's not from Yookassa.",
        #         ip,
        #     )
        #     raise AuthenticationFailed("Wrong client IP. Bad Request.")
