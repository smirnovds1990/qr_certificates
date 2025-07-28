from rest_framework.generics import ListAPIView

from api.v1.serializers import CertificateListSerializer
from orders.models import Certificate


class CertificateListView(ListAPIView):
    """Получить все доступные для продажи сертификаты."""

    queryset = Certificate.objects.filter(is_active=True)
    serializer_class = CertificateListSerializer
