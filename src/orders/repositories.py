from uuid import UUID

from orders.exceptions import (
    CertificateDesignNotFoundError,
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
    CertificateOrderStatusValidationError,
)
from orders.models import (
    Certificate,
    CertificateDesign,
    CertificateOrder,
    Customer,
    OrderStatus,
)


def get_certificate_by_id(id: UUID) -> Certificate:
    try:
        return Certificate.objects.get(id=id)
    except Certificate.DoesNotExist:
        raise CertificateNotFoundError(f"Certificate with id: {id} not found.")


def get_design_by_id(id: UUID) -> CertificateDesign:
    try:
        return CertificateDesign.objects.get(id=id)
    except CertificateDesign.DoesNotExist:
        raise CertificateDesignNotFoundError(
            f"Certificate design with id: {id} not found."
        )


def create_or_get_customer(
    first_name: str, last_name: str, phone: str
) -> Customer:
    customer, created = Customer.objects.get_or_create(
        first_name=first_name, last_name=last_name, phone=phone
    )
    return customer


def create_certificate_order(
    certificate: Certificate,
    design: CertificateDesign,
    email: str,
    customer: Customer,
) -> CertificateOrder:
    return CertificateOrder.objects.create(
        certificate=certificate,
        design=design,
        email=email,
        customer=customer,
    )


def refresh_certificate_order_status(order_id: UUID, new_status: str) -> None:
    if new_status not in OrderStatus.values:
        raise CertificateOrderStatusValidationError(
            f"Unknown status for a CertificateOrder: {new_status}"
        )
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
