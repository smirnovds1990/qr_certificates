from uuid import uuid4

import pytest

from orders.exceptions import (
    CertificateNotFoundError,
    CertificateOrderNotFoundError,
)
from orders.models import Certificate, CertificateOrder, Customer
from orders.repositories import (
    create_certificate_order,
    create_or_get_customer,
    get_certificate_by_id,
    refresh_certificate_order_status,
)


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


def test_create_or_get_customer_when_customer_doesnt_exist(
    customer_data: dict[str, str],
) -> None:
    assert Customer.objects.count() == 0
    new_customer = create_or_get_customer(**customer_data)
    assert Customer.objects.count() == 1
    assert new_customer.first_name == customer_data["first_name"]
    assert new_customer.last_name == customer_data["last_name"]
    assert new_customer.phone == customer_data["phone"]


def test_create_or_get_customer_when_customer_exists(
    customer_data: dict[str, str],
    customer: Customer,
) -> None:
    count_before = Customer.objects.count()
    existing_customer = create_or_get_customer(**customer_data)
    assert Customer.objects.count() == count_before
    assert customer.id == existing_customer.id


def test_create_certificate_order(
    certificate_order_data: dict[str, Certificate | str | Customer],
) -> None:
    assert CertificateOrder.objects.count() == 0
    new_order = create_certificate_order(**certificate_order_data)
    assert CertificateOrder.objects.count() == 1
    assert new_order.certificate == certificate_order_data["certificate"]
    assert new_order.email == "test@test.com"
    assert new_order.customer == certificate_order_data["customer"]


@pytest.mark.parametrize("new_status", ["succeeded", "canceled", "unknown"])
def test_refresh_certificate_order_status(
    certificate_order: CertificateOrder, new_status: str
) -> None:
    status_before = certificate_order.status
    assert status_before not in ["succeeded", "canceled"]
    refresh_certificate_order_status(certificate_order.id, new_status)
    certificate_order.refresh_from_db()
    assert certificate_order.status == new_status


@pytest.mark.parametrize("new_status", ["succeeded", "canceled"])
def test_refresh_certificate_order_status_with_wrong_order_id(
    new_status: str,
) -> None:
    fake_uuid = uuid4()
    with pytest.raises(CertificateOrderNotFoundError):
        refresh_certificate_order_status(fake_uuid, new_status)
