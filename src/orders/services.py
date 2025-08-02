import logging
import os
from io import BytesIO
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

import qrcode
from django.conf import settings
from django.core.mail import EmailMessage

from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
    UnexpectedYokassaNotificationStatus,
)
from orders.models import CertificateOrder, OrderStatus
from orders.repositories import (
    create_certificate_order,
    get_certificate_by_id,
    get_order_by_id,
    make_certificate_order_used,
    refresh_certificate_order_status,
)
from yookassa_services.services import create_payment


logger = logging.getLogger(__name__)


def _get_yookassa_notification_status(data: dict[str, Any]) -> str:
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
        raise UnexpectedYokassaNotificationStatus(
            f"Unknown status {data["object"]["status"]} "
            f"for event {data["event"]}"
        )


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


def process_certificate_order(data: dict[str, UUID | str]) -> str:
    """
    Находит выбранный пользователем сертификат.
    Создает заказ с ним в статусе Pending.
    Возвращает URL ЮКассы для оплаты.
    """
    try:
        certificate = get_certificate_by_id(id=data["id"])
        new_order = create_certificate_order(
            certificate=certificate, email=data["email"]
        )
        logger.info("New order created: %s", str(new_order))
        payment = create_payment(
            value=certificate.value,
            description=str(new_order),
            order_id=new_order.id,
        )
        logger.info("Payment created for a new order: %s", str(new_order))
        return payment.confirmation["confirmation_url"]
    except CertificateNotFoundError as error:
        logger.warning(
            "Certificate not found! id: %s, error: %s", data["id"], error
        )
        raise


def send_certificate_to_client(order_id: UUID) -> None:
    BASE_URL = os.getenv("BASE_URL")
    order = get_order_by_id(order_id)
    certificate_url = urljoin(BASE_URL, f"{order_id}/")
    image = qrcode.make(certificate_url)
    with BytesIO() as buffer:
        image.save(buffer, bitmap_format="png")
        buffer.seek(0)
        email = EmailMessage(
            subject="Ваш QR-сертификат",
            body=(
                "Приобретённый вами сертификат "
                f"на сумму {order.certificate.value} во вложении. "
                "Спасибо!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach("qr_certificate.png", buffer.read(), "image/png")
        email.send()


def process_yookassa_notification(data: dict[str, Any]) -> None:
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
            send_certificate_to_client(order_id)
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", data["id"], error)
        raise


def get_certificate_order_info(id: UUID) -> dict[str, Any]:
    try:
        order = get_order_by_id(id)
        return _form_order_info(order)
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", id, error)
        raise


def use_certificate(id: UUID) -> dict[str, Any]:
    try:
        order = get_order_by_id(id)
        order_info = _form_order_info(order)
        if not order.status == OrderStatus.PAID or order.is_used:
            return order_info
        changed_order = make_certificate_order_used(order)
        order_info["is_used"] = changed_order.is_used
        order_info["messages"]["is_used"] = "Сертификат списан успешно."
        return order_info
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", id, error)
        raise
