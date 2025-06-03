from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("course/<slug:course_slug>/checkout/",
         views.CourseCheckoutView.as_view(),
         name="course_checkout"),
    path("subscription/<int:subscription_type_id>/checkout/",
         views.SubscriptionCheckoutView.as_view(),
         name="subscription_checkout"),
    path("success/", views.PaymentSuccessView.as_view(), name="payment_success"),
    path("cancel/", views.PaymentCancelView.as_view(), name="payment_cancel"),
    path("webhook/", views.StripeWebhookView.as_view(), name="stripe_webhook"),
]
