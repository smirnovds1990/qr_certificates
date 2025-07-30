import os
from uuid import uuid4

from yookassa import Configuration, Payment
from yookassa.domain.response import PaymentResponse

from yookassa_services.constants import (
    CURRENCY_RUB,
    REDIRECT_CONFIRMATION_TYPE,
)


Configuration.account_id = os.getenv("YOOKASSA_ACCOUNT_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


def create_payment(value: int, description: str) -> PaymentResponse:
    return Payment.create(
        {
            "amount": {"value": f"{value:.2f}", "currency": CURRENCY_RUB},
            "confirmation": {
                "type": REDIRECT_CONFIRMATION_TYPE,
                "return_url": os.getenv("RETURN_URL"),
            },
            "capture": True,
            "description": description,
        },
        idempotency_key=uuid4(),
    )
