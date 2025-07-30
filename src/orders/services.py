import logging
from uuid import UUID

from orders.exceptions import CertificateNotFoundError
from orders.repositories import (
    create_certificate_order,
    get_certificate_by_id,
)
from yookassa_services.services import create_payment


logger = logging.getLogger(__name__)


def process_certificate_order(data: dict[str, UUID | str]) -> str:
    try:
        certificate = get_certificate_by_id(id=data["id"])
        new_order = create_certificate_order(
            certificate=certificate, email=data["email"]
        )
        logger.info("New order created: %s", str(new_order))
        payment = create_payment(
            value=certificate.value, description=str(new_order)
        )
        payment.metadata["order_id"] = new_order.id
        logger.info("Payment created for a new order: %s", str(new_order))
        return payment.confirmation["confirmation_url"]
    except CertificateNotFoundError as error:
        logger.warning(
            "Certificate not found! id: %s, error: %s", data["id"], error
        )
        raise
