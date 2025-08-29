from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.html import format_html

from orders.models import (
    Certificate,
    CertificateDesign,
    CertificateOrder,
    Customer,
)
from orders.services import send_message_to_client


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


@admin.register(CertificateDesign)
class CertificateDesignAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "image_preview"]
    list_filter = ["name"]
    readonly_fields = ["image_preview"]

    @admin.display(description="Превью")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "—"


@admin.register(CertificateOrder)
class CertificateOrderAdmin(admin.ModelAdmin):
    list_display = [
        "certificate",
        "email",
        "is_used",
        "status",
        "created_at",
        "customer",
        "send_button",
        "certificate_design",
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
    readonly_fields = [
        "status",
        "created_at",
        "updated_at",
        "certificate_design",
    ]

    @admin.display(description="Отправка")
    def send_button(self, obj):
        return format_html(
            '<a class="button" style="width:80px; display:inline-block;'
            'text-align:center;" href="{}">Отправить сертификат</a>',
            f"/admin/orders/certificateorder/{obj.id}/send/",
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<uuid:order_id>/send/",
                self.admin_site.admin_view(self.send_certificate_view),
                name="certificateorder-send",
            ),
        ]
        return custom_urls + urls

    def send_certificate_view(self, request, order_id):
        order = get_object_or_404(CertificateOrder, id=order_id)
        send_message_to_client(order_id)
        self.message_user(request, f"Сертификат для {order.email} отправлен!")
        return redirect("/admin/orders/certificateorder/")

    @admin.display(description="Дизайн сертификата")
    def certificate_design(self, obj):
        if obj.design:
            return format_html(
                '<img src="{}" width="100" />', obj.design.image.url
            )
        return "—"
