from rest_framework import serializers

from orders.models import Certificate, CertificateDesign


class CertificateListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = ("id", "value")


class CertificateOrderCreateSerializer(serializers.Serializer):
    """Для данных, выбранных пользователем при покупке сертификата."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=15)


class YookassaNotificationObjectSerializer(serializers.Serializer):
    """Для вложенного в уведомление object."""

    status = serializers.CharField()
    metadata = serializers.DictField()


class YookassaNotificationSerializer(serializers.Serializer):
    """Для объекта уведомления о смене статуса платежа от ЮКассы."""

    type = serializers.CharField()
    event = serializers.CharField()
    object = YookassaNotificationObjectSerializer()


class UrlResponseSerializer(serializers.Serializer):
    """Для возврата URL от ЮКассы."""

    confirmation_url = serializers.URLField()


class NestedMessagesSerializer(serializers.Serializer):
    """Для вложенных сообщений при списании заказа."""

    is_used = serializers.CharField(required=False)
    status = serializers.CharField(required=False)


class CertificateOrderInfoSerializer(serializers.Serializer):
    """Для возврата информации о заказе при сканировании QR-сертификата."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    certificate_value = serializers.IntegerField()
    is_used = serializers.BooleanField()
    status = serializers.CharField()
    messages = NestedMessagesSerializer()


class CertificateDesignListSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = CertificateDesign
        fields = ("name", "image")
