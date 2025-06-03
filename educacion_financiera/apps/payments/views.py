import json
import stripe
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from educacion_financiera.apps.courses.models import Course, Enrollment
from educacion_financiera.apps.subscriptions.models import Subscription, SubscriptionType
from .models import Payment


# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class CourseCheckoutView(LoginRequiredMixin, TemplateView):
    """
    Handle checkout process for a course
    """
    template_name = "apps/payments/course_checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the course
        course_slug = self.kwargs.get("course_slug")
        course = get_object_or_404(Course, slug=course_slug)

        # Check if user already enrolled
        is_enrolled = Enrollment.objects.filter(
            course=course,
            student=self.request.user,
            active=True
        ).exists()

        if is_enrolled:
            # If already enrolled, redirect to course
            return redirect("courses:course_detail", slug=course.slug)

        # Free course doesn't need payment
        if course.price <= 0:
            # Create enrollment directly
            Enrollment.objects.create(
                course=course,
                student=self.request.user,
                active=True
            )
            return redirect("courses:course_detail", slug=course.slug)

        # For paid courses, set up payment
        context["course"] = course
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY

        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": course.title,
                            "description": f"Enrollment in {course.title}",
                        },
                        "unit_amount": int(course.price * 100),  # Convert to cents
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=self.request.build_absolute_uri(
                reverse("payments:payment_success")
            ),
            cancel_url=self.request.build_absolute_uri(
                reverse("payments:payment_cancel")
            ),
            client_reference_id=f"course_{course.id}_{self.request.user.id}",
            customer_email=self.request.user.email,
            metadata={
                "payment_type": "course",
                "course_id": course.id,
                "user_id": self.request.user.id,
            },
        )

        context["checkout_session_id"] = checkout_session.id

        # Create a pending payment record
        payment = Payment.objects.create(
            user=self.request.user,
            payment_type="course",
            amount=course.price,
            status="pending",
            provider="stripe",
            provider_payment_id=checkout_session.id,
            course=course,
            metadata={
                "session_id": checkout_session.id,
                "course_id": course.id,
            }
        )

        context["payment"] = payment

        return context


class SubscriptionCheckoutView(LoginRequiredMixin, TemplateView):
    """
    Handle checkout process for a subscription
    """
    template_name = "apps/payments/subscription_checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the subscription type
        subscription_type_id = self.kwargs.get("subscription_type_id")
        subscription_type = get_object_or_404(SubscriptionType, id=subscription_type_id)

        # Check if user already has an active subscription of this type
        active_subscription = Subscription.objects.filter(
            user=self.request.user,
            subscription_type=subscription_type,
            status="active"
        ).exists()

        if active_subscription:
            # If already has active subscription, redirect to dashboard
            return redirect("users:detail", pk=self.request.user.id)

        # Free subscription doesn't need payment
        if subscription_type.price <= 0:
            # Create subscription directly
            Subscription.objects.create(
                user=self.request.user,
                subscription_type=subscription_type,
                status="active",
                start_date=timezone.now(),
                end_date=(timezone.now() + timedelta(days=subscription_type.duration_days)) if subscription_type.duration_days > 0 else None
            )
            return redirect("users:detail", pk=self.request.user.id)

        # For paid subscriptions, set up payment
        context["subscription_type"] = subscription_type
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY

        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": subscription_type.name,
                            "description": subscription_type.description,
                        },
                        "unit_amount": int(subscription_type.price * 100),  # Convert to cents
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=self.request.build_absolute_uri(
                reverse("payments:payment_success")
            ),
            cancel_url=self.request.build_absolute_uri(
                reverse("payments:payment_cancel")
            ),
            client_reference_id=f"subscription_{subscription_type.id}_{self.request.user.id}",
            customer_email=self.request.user.email,
            metadata={
                "payment_type": "subscription",
                "subscription_type_id": subscription_type.id,
                "user_id": self.request.user.id,
                "duration_days": subscription_type.duration_days,
            },
        )

        context["checkout_session_id"] = checkout_session.id

        # Create a subscription record (pending)
        subscription = Subscription.objects.create(
            user=self.request.user,
            subscription_type=subscription_type,
            status="pending",
        )

        # Create a pending payment record
        payment = Payment.objects.create(
            user=self.request.user,
            payment_type="subscription",
            amount=subscription_type.price,
            status="pending",
            provider="stripe",
            provider_payment_id=checkout_session.id,
            subscription=subscription,
            metadata={
                "session_id": checkout_session.id,
                "subscription_type_id": subscription_type.id,
                "duration_days": subscription_type.duration_days,
            }
        )

        context["payment"] = payment
        context["subscription"] = subscription

        return context


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """
    Handle successful payment
    """
    template_name = "apps/payments/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The actual payment processing is done in the webhook
        # This view is just to show a success message
        return context


class PaymentCancelView(LoginRequiredMixin, TemplateView):
    """
    Handle cancelled payment
    """
    template_name = "apps/payments/payment_cancel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Could update payment status if needed
        return context


class StripeWebhookView(View):
    """
    Handle Stripe webhook events
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the event
        if event.type == "checkout.session.completed":
            # Payment was successful
            session = event.data.object

            # Get client reference id
            client_reference_id = session.get("client_reference_id", "")

            if client_reference_id.startswith("course_"):
                # Course payment
                parts = client_reference_id.split("_")
                if len(parts) >= 3:
                    course_id = int(parts[1])
                    user_id = int(parts[2])

                    # Update payment status
                    payment = get_object_or_404(
                        Payment,
                        provider_payment_id=session.id,
                        payment_type="course"
                    )
                    payment.status = "completed"
                    payment.provider_transaction_id = session.payment_intent
                    payment.save()

                    # Create enrollment
                    course = get_object_or_404(Course, id=course_id)
                    user = get_object_or_404(settings.AUTH_USER_MODEL, id=user_id)

                    Enrollment.objects.create(
                        course=course,
                        student=user,
                        active=True
                    )

            elif client_reference_id.startswith("subscription_"):
                # Subscription payment
                parts = client_reference_id.split("_")
                if len(parts) >= 3:
                    subscription_type_id = int(parts[1])
                    user_id = int(parts[2])

                    # Update payment status
                    payment = get_object_or_404(
                        Payment,
                        provider_payment_id=session.id,
                        payment_type="subscription"
                    )
                    payment.status = "completed"
                    payment.provider_transaction_id = session.payment_intent
                    payment.save()

                    # Update subscription status
                    subscription = payment.subscription
                    subscription.status = "active"
                    subscription.start_date = timezone.now()

                    # Set end date if duration is specified
                    if subscription.subscription_type.duration_days > 0:
                        subscription.end_date = timezone.now() + timedelta(
                            days=subscription.subscription_type.duration_days
                        )

                    subscription.save()

        return HttpResponse(status=200)
