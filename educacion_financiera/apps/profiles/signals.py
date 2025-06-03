from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile instance for newly created User instances
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure profile is saved when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist
        # (in case this is a migrated user)
        Profile.objects.create(user=instance)
