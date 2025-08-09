from uuid import uuid4

import pytest

from orders.exceptions import CertificateNotFoundError
from orders.models import Certificate
from orders.repositories import get_certificate_by_id


pytestmark = pytest.mark.django_db


def test_get_certificate_by_id(
    two_certificates: tuple[Certificate, Certificate],
) -> None:
    id = two_certificates[0].id
    found_certificate = get_certificate_by_id(id)
    assert id == found_certificate.id


def test_get_certificate_by_id_with_wrong_id() -> None:
    fake_id = uuid4()
    with pytest.raises(CertificateNotFoundError):
        get_certificate_by_id(fake_id)
