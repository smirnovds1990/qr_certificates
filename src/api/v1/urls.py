from django.urls import path

from api.v1.views import CertificateListView


urlpatterns = [
    path("certificates/", CertificateListView.as_view(), name="certificates"),
]
