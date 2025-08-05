from django.contrib import admin

from orders.models import Certificate, CertificateOrder, Customer


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["value", "is_active"]
    list_filter = ["value", "is_active"]
    search_fields = ["value"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone"]
    list_filter = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name", "phone"]


@admin.register(CertificateOrder)
class CertificateOrderAdmin(admin.ModelAdmin):
    list_display = [
        "certificate",
        "email",
        "is_used",
        "status",
        "created_at",
        "customer",
    ]
    list_filter = [
        "certificate",
        "email",
        "is_used",
        "status",
        "created_at",
        "customer",
    ]
    search_fields = ["email", "created_at"]
    readonly_fields = ["is_used", "status", "created_at", "updated_at"]
