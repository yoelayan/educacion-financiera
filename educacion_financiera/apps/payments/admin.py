from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "provider_payment_id",
        "user",
        "payment_type",
        "amount",
        "currency",
        "status",
        "provider",
        "created"
    ]
    list_filter = ["status", "payment_type", "provider", "created"]
    search_fields = [
        "provider_payment_id",
        "provider_transaction_id",
        "user__email"
    ]
    readonly_fields = ["created", "modified"]
    date_hierarchy = "created"
    raw_id_fields = ["user", "subscription", "course"]
    fieldsets = (
        (None, {
            "fields": (
                "user",
                "payment_type",
                ("amount", "currency"),
                "status"
            )
        }),
        (_("Provider Details"), {
            "fields": (
                "provider",
                "provider_payment_id",
                "provider_transaction_id"
            )
        }),
        (_("Related Objects"), {
            "fields": ("subscription", "course")
        }),
        (_("Metadata"), {
            "fields": ("metadata", "created", "modified")
        }),
    )
