import pytest

from orders.models import Certificate
from orders.repositories import get_certificate_by_id


pytestmark = pytest.mark.django_db


def test_get_certificate_by_id(
    two_certificates: tuple[Certificate, Certificate],
) -> None:
    id = two_certificates[0].id
    found_certificate = get_certificate_by_id(id)
    assert id == found_certificate.id
