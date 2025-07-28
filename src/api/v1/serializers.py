from rest_framework.serializers import ModelSerializer

from orders.models import Certificate


class CertificateListSerializer(ModelSerializer):

    class Meta:
        model = Certificate
        fields = ("value",)
