"""
Этот модуль предоставляет схемы для типизации используемых сложных объектов.
"""

from typing import Any, TypedDict
from uuid import UUID


class CertificateOrderFormScheme(TypedDict):
    """Для данных из формы покупки сертификата."""

    certificate_id: UUID
    design_id: UUID
    email: str
    first_name: str
    last_name: str
    phone: str


class YookassaNotificationObjectScheme(TypedDict):
    """Для вложенного в уведомление объекта — `object`."""

    status: str
    metadata: dict[str, Any]


class YookassaNotificationScheme(TypedDict):
    """Для данных в уведомлениях от ЮКассы."""

    type: str
    event: str
    object: YookassaNotificationObjectScheme
