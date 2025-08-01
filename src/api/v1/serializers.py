from rest_framework import serializers

from orders.models import Certificate


class CertificateListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Certificate
        fields = ("id", "value")


class CertificateOrderCreateSerializer(serializers.Serializer):
    """Для данных, выбранных пользователем при покупке сертификата."""

    id = serializers.UUIDField()
    email = serializers.EmailField()


class YookassaNotificationObjectSerializer(serializers.Serializer):
    """Для вложенного в уведомление object."""

    status = serializers.CharField()
    metadata = serializers.DictField()


class YookassaNotificationSerializer(serializers.Serializer):
    """Для объекта уведомления о смене статуса платежа от ЮКассы."""

    type = serializers.CharField()
    event = serializers.CharField()
    object = YookassaNotificationObjectSerializer()


class CertificateOrderInfoSerializer(serializers.Serializer):
    """Для возврата информации о заказе при сканировании QR-сертификата."""

    email = serializers.EmailField()
    certificate_value = serializers.IntegerField()
    message = serializers.CharField(required=False)
