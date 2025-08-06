from uuid import uuid4

from django.core.validators import StepValueValidator  # type: ignore
from django.db import models


class OrderStatus(models.TextChoices):
    """Возможные стадии заказа, в зависимости от статуса оплаты."""

    PENDING = "Pending", "В процессе"
    PAID = "Paid", "Оплачен"
    CANCELLED = "Cancelled", "Отменен"


class Certificate(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    value = models.PositiveIntegerField(
        verbose_name="Номинал",
        validators=[StepValueValidator(1000)],
        blank=False,
        null=False,
        unique=True,
        help_text="Введите номинал, кратно 1000 ₽",
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True,
        help_text="Показывает будет ли сертификат доступен для покупки",
    )

    class Meta:
        verbose_name = "Сетификат"
        verbose_name_plural = "Сертификаты"
        ordering = ["value"]

    def __str__(self) -> str:
        return f"{self.value} ₽"


class Customer(models.Model):
    first_name = models.CharField(
        verbose_name="Имя", max_length=150, blank=False, null=False
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=150, blank=False, null=False
    )
    phone = models.CharField(
        verbose_name="Номер телефона", max_length=15, blank=False, null=False
    )

    class Meta:
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"
        ordering = ["last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}. Телефон: {self.phone}"


class CertificateOrder(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.PROTECT,
        verbose_name="Сертификат",
        related_name="orders",
        help_text="Выберите сертификат",
    )
    email = models.EmailField(
        verbose_name="Email для отправки",
        blank=False,
        null=False,
        help_text="Введите email, на который будет отправлен сертификат",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name="Покупатель",
        related_name="orders",
        help_text="Выберите покупателя",
    )
    is_used = models.BooleanField(
        verbose_name="Использован",
        default=False,
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Заказ сертификата"
        verbose_name_plural = "Заказы сертификатов"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"Заказ от {self.created_at:%d-%m-%Y  %H:%M}."
            f"  Для '{self.email}',"
            f" на сумму — {self.certificate.value} ₽"
        )
