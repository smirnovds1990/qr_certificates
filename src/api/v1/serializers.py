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
