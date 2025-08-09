import pytest

from orders.models import Certificate


@pytest.fixture
def two_certificates(db) -> tuple[Certificate, Certificate]:
    first_certificate = Certificate.objects.create(value=1000)
    second_certificate = Certificate.objects.create(value=2000)
    return first_certificate, second_certificate
