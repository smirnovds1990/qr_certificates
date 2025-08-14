import pytest

from orders.models import Certificate, CertificateOrder, Customer


@pytest.fixture
def two_certificates(db) -> tuple[Certificate, Certificate]:
    first_certificate = Certificate.objects.create(value=1000)
    second_certificate = Certificate.objects.create(value=2000)
    return first_certificate, second_certificate


@pytest.fixture
def customer_data() -> dict[str, str]:
    return {
        "first_name": "Test",
        "last_name": "Testovich",
        "phone": "+79804321111",
    }


@pytest.fixture
def customer(db, customer_data) -> Customer:
    return Customer.objects.create(**customer_data)


@pytest.fixture
def certificate(db) -> Certificate:
    return Certificate.objects.create(value=1000)


@pytest.fixture
def certificate_order_data(
    customer, certificate
) -> dict[str, Certificate | str | Customer]:
    return {
        "certificate": certificate,
        "email": "test@test.com",
        "customer": customer,
    }


@pytest.fixture
def certificate_order(db, certificate_order_data) -> CertificateOrder:
    return CertificateOrder.objects.create(**certificate_order_data)
