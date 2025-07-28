from rest_framework.serializers import ModelSerializer

from orders.models import Certificate


class CertificateListSerializer(ModelSerializer):
    """Выдает все сертификаты доступные для продажи."""

    class Meta:
        model = Certificate
        fields = ("value",)
