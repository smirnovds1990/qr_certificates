from uuid import UUID

from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
)
from orders.models import Certificate, CertificateOrder


def get_certificate_by_id(id: UUID) -> Certificate:
    try:
        return Certificate.objects.get(id=id)
    except Certificate.DoesNotExist:
        raise CertificateNotFoundError(f"Certificate with id: {id} not found.")


def create_certificate_order(
    certificate: Certificate, email: str
) -> CertificateOrder:
    return CertificateOrder.objects.create(
        certificate=certificate, email=email
    )


def refresh_certificate_order_status(order_id: UUID, new_status: str) -> None:
    try:
        order = CertificateOrder.objects.get(id=order_id)
        order.status = new_status
        order.save()
    except CertificateOrder.DoesNotExist:
        raise CertificateOrderNotFoundError(f"Order with id: {id} not found.")


def get_order_by_id(id: UUID) -> CertificateOrder:
    try:
        return CertificateOrder.objects.get(id=id)
    except CertificateOrder.DoesNotExist:
        raise CertificateOrderNotFoundError(f"Order with id: {id} not found.")
