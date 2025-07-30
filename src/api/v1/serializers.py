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
