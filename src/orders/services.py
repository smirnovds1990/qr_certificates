import logging
from typing import Any
from uuid import UUID

from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
    UnexpectedYokassaNotificationStatus,
)
from orders.models import OrderStatus
from orders.repositories import (
    create_certificate_order,
    get_certificate_by_id,
    get_order_by_id,
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


def process_yookassa_notification(data: dict[str, Any]) -> None:
    """
    Проверяет статус платежа, изменяет статус заказа в соответствии с ним.
    """
    expected_statuses = {
        "succeeded": OrderStatus.PAID,
        "canceled": OrderStatus.CANCELLED,
    }
    notification_status = _get_yookassa_notification_status(data)
    try:
        refresh_certificate_order_status(
            order_id=data["object"]["metadata"]["order_id"],
            new_status=expected_statuses[notification_status],
        )
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", data["id"], error)
        raise


def get_certificate_order_info(id: UUID) -> dict[str, dict[str, str | int]]:
    try:
        order = get_order_by_id(id)
        order_info = {
            "email": order.email,
            "certificate_value": order.certificate.value,
        }
        if order.is_used:
            order_info["message"] = "Этот сертификат уже использован."
        return order_info
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", id, error)
        raise
