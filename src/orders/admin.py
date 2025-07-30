from django.contrib import admin

from orders.models import Certificate, CertificateOrder


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["value", "is_active"]
    list_filter = ["value", "is_active"]
    search_fields = ["value"]


@admin.register(CertificateOrder)
class CertificateOrderAdmin(admin.ModelAdmin):
    list_display = ["certificate", "email", "is_used", "status", "created_at"]
    list_filter = ["certificate", "email", "is_used", "status", "created_at"]
    search_fields = ["email", "created_at"]
    readonly_fields = ["is_used", "status", "created_at", "updated_at"]
