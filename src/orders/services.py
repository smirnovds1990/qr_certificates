import logging
import os
import smtplib
import socket
import ssl
from email.mime.image import MIMEImage
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db import IntegrityError, transaction

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
    get_design_by_id,
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
    if order.design is None:
        design = "Нет изображения"
    else:
        design = order.design.image.url
    order_info = {
        "id": order.id,
        "email": order.email,
        "certificate_value": order.certificate.value,
        "certificate_design": design,
        "is_used": order.is_used,
        "status": order.status,
        "messages": {},
    }
    if order.is_used:
        order_info["messages"]["is_used"] = "Этот сертификат уже использован."
    if not order.status == OrderStatus.PAID:
        order_info["messages"]["status"] = "Сертификат не олачен."
    return order_info


def process_certificate_order(data: CertificateOrderFormScheme) -> str:
    """
    Находит выбранный пользователем сертификат.
    Создает заказ с ним в статусе Pending.
    Возвращает URL ЮКассы для оплаты.
    """
    try:
        certificate = get_certificate_by_id(id=data["certificate_id"])
        design = get_design_by_id(id=data["design_id"])
        with transaction.atomic():
            customer = create_or_get_customer(
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
            )
            new_order = create_certificate_order(
                certificate=certificate,
                design=design,
                email=data["email"],
                customer=customer,
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
            "Certificate not found! id: %s, error: %s",
            data["certificate_id"],
            error,
        )
        raise CertificateNotFoundError()
    except IntegrityError as error:
        logger.warning("An error while creating an order: %s", error)
        raise CertificateOrderCreateError()


def send_message_to_client(order_id: UUID) -> None:
    order = get_order_by_id(order_id)
    text_content = "\n".join(
        [
            MESSAGE,
            "https://certificates-qr-vgrs.vercel.app/certificates/"
            f"{order_id}\n\n"
            f"Номинал: {order.certificate.value}\n",
            MESSAGE_INSTRUCTION.replace("\n", "<br>"),
        ]
    )
    html_content = f"""
    <p>{MESSAGE}</p>
    <p>
      <a href="https://certificates-qr-vgrs.vercel.app/certificates/{order_id}">
          Перейти к сертификату
      </a>
    </p>
    <p>Номинал: {order.certificate.value} ₽</p>
    <p><img src="cid:design_img" width="600" alt="Сертификат"></p>
    <p>{MESSAGE_INSTRUCTION}</p>
    """
    email_message = EmailMultiAlternatives(
        subject="Вам подарок от HOME",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email_message.attach_alternative(html_content, "text/html")
    try:
        image_path = order.design.image.path
        with open(image_path, "rb") as file:
            img = MIMEImage(file.read())
            img.add_header("Content-ID", "<design_img>")
            img.add_header(
                "Content-Disposition",
                "inline",
                filename=os.path.basename(image_path),
            )
            email_message.attach(img)
    except FileNotFoundError:
        logger.warning(
            "Не удалось прикрепить картинку: %s", order.design.image
        )
    try:
        email_message.send()
    except (smtplib.SMTPException, socket.error, ssl.SSLError) as error:
        logger.warning("Ошибка при отправке письма клиенту. %s", error)
        raise SendEmailError()


def send_message_to_admin(order_id: UUID) -> None:
    order = get_order_by_id(order_id)
    message_content = "\n".join(
        [
            "Куплен новый сертификат.\n",
            f"Имя: {order.customer.first_name}\n"
            f"Фамилия: {order.customer.last_name}\n"
            f"Телефон: {order.customer.phone}\n"
            f"Email: {order.email}\n"
            f"Сумма: {order.certificate.value}\n"
            f"Дата и время покупки: {order.created_at}\n",
        ]
    )
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        logger.warning(
            "ADMIN_EMAIL не задан, письмо администратору не отправлено"
        )
        return
    email_message = EmailMessage(
        subject="Куплен новый сертификат.",
        body=message_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[admin_email],
    )
    try:
        email_message.send()
        logger.info(
            "Сообщение админу отправлено, почта админа: %s", admin_email
        )
    except (smtplib.SMTPException, socket.error, ssl.SSLError) as error:
        logger.warning("Ошибка при отправке письма администратору. %s", error)
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
            send_message_to_admin(order_id)
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", order_id, error)
        raise CertificateOrderNotFoundError()


def get_certificate_order_info(id: UUID) -> dict[str, Any]:
    try:
        order = get_order_by_id(id)
        return _form_order_info(order)
    except CertificateOrderNotFoundError as error:
        logger.warning("Order not found! id: %s, error: %s", id, error)
        raise CertificateOrderNotFoundError()
