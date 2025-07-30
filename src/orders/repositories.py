from uuid import UUID

from orders.exceptions import CertificateNotFoundError
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
