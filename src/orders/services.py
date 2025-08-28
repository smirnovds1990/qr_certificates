import logging
import smtplib
import socket
import ssl

# from io import BytesIO
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

import qrcode
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from qrcode.image.pil import PilImage

from orders.constants import MESSAGE, MESSAGE_INSTRUCTION
from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderCreateError,
    CertificateOrderNotFoundError,
    NoConfirmationReturnedError,
    SendEmailError,
    UnexpectedYokassaNotificationStatusError,
)
from orders.models import CertificateOrder, OrderStatus
from orders.repositories import (
    create_certificate_order,
    create_or_get_customer,
    get_certificate_by_id,
    get_order_by_id,
    refresh_certificate_order_status,
)
from orders.types import CertificateOrderFormScheme, YookassaNotificationScheme
from yookassa_services.services import create_payment


logger = logging.getLogger(__name__)


def _get_yookassa_notification_status(data: YookassaNotificationScheme) -> str:
    if (
        data["event"] == "payment.succeeded"
        and data["object"]["status"] == "succeeded"
    ):
        return "succeeded"
    elif (
        data["event"] == "payment.canceled"
        and data["object"]["status"] == "canceled"
    ):
        return "canceled"
    else:
        logger.warning(
            "Unknown status %s for event %s.",
            data["object"]["status"],
            data["event"],
        )
        raise UnexpectedYokassaNotificationStatusError()


def _form_order_info(order: CertificateOrder) -> dict[str, Any]:
    order_info = {
        "email": order.email,
        "certificate_value": order.certificate.value,
        "is_used": order.is_used,
        "status": order.status,
        "messages": {},
    }
    if order.is_used:
        order_info["messages"]["is_used"] = "Этот сертификат уже использован."
    if not order.status == OrderStatus.PAID:
        order_info["messages"]["status"] = "Сертификат не олачен."
    return order_info


def _create_qr_code_with_order_url(order_id: UUID) -> PilImage:
    certificate_url = urljoin(settings.BASE_URL, f"{order_id}/change/")
    return qrcode.make(certificate_url, image_factory=PilImage)


def process_certificate_order(data: CertificateOrderFormScheme) -> str:
    """
    Находит выбранный пользователем сертификат.
    Создает заказ с ним в статусе Pending.
    Возвращает URL ЮКассы для оплаты.
    """
    try:
        certificate = get_certificate_by_id(id=data["id"])
        with transaction.atomic():
            customer = create_or_get_customer(
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
            )
            new_order = create_certificate_order(
                certificate=certificate, email=data["email"], customer=customer
            )
            logger.info("New order created: %s", str(new_order))
        payment = create_payment(
            value=certificate.value,
            description=str(new_order),
            order_id=new_order.id,
        )
        logger.info("Payment created for a new order: %s", str(new_order))
        if payment.confirmation is None:
            raise NoConfirmationReturnedError()
        return payment.confirmation["confirmation_url"]
    except CertificateNotFoundError as error:
        logger.warning(
            "Certificate not found! id: %s, error: %s", data["id"], error
        )
        raise CertificateNotFoundError()
    except IntegrityError as error:
        logger.warning("An error while creating an order: %s", error)
        raise CertificateOrderCreateError()


def send_message_to_client(order_id: UUID) -> None:
    order = get_order_by_id(order_id)
    # image = _create_qr_code_with_order_url(order_id)
    # Сгенерировать ссылку на фронтенд, чтобы прикрепить ее к письму
    email = EmailMessage(
        subject="Вам подарок от HOME",
        body=(
            "\n".join(
                [
                    MESSAGE,
                    f"http://localhost:5173/certificates/{order_id}\n"
                    f"Номинал: {order.certificate.value}\n",
                    MESSAGE_INSTRUCTION,
                ]
            )
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    try:
        email.send()
        # with BytesIO() as buffer:
        #     image.save(buffer, format="PNG")
        #     buffer.seek(0)
        #     email.attach(f"{order.id}.png", buffer.read(), "image/png")
        #     email.send()
    except (smtplib.SMTPException, socket.error, ssl.SSLError) as error:
        logger.warning("Ошибка при отправке письма клиенту. %s", error)
        raise SendEmailError()


def process_yookassa_notification(data: YookassaNotificationScheme) -> None:
    """
    Проверяет статус платежа, изменяет статус заказа в соответствии с ним.
    Создает QR-сертификат и отправляет клиенту, если оплата успешна.
    """
    expected_statuses = {
        "succeeded": OrderStatus.PAID,
        "canceled": OrderStatus.CANCELLED,
    }
    order_id = data["object"]["metadata"]["order_id"]
    notification_status = _get_yookassa_notification_status(data)
    try:
        refresh_certificate_order_status(
            order_id=order_id,
            new_status=expected_statuses[notification_status],
        )
        if notification_status == "succeeded":
            send_message_to_client(order_id)
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", order_id, error)
        raise CertificateOrderNotFoundError()
