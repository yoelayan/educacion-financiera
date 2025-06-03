from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Subscription, SubscriptionType


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "duration_days", "is_active"]
    list_filter = ["is_active", "created"]
    search_fields = ["name", "description"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "subscription_type", "status", "start_date", "end_date", "is_trial"]
    list_filter = ["status", "is_trial", "subscription_type", "created"]
    search_fields = ["user__email", "payment_id"]
    date_hierarchy = "created"
    raw_id_fields = ["user"]
