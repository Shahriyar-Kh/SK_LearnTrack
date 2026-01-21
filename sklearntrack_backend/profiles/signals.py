# FILE: profiles/signals.py
# ============================================================================

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile, NotificationSettings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create Profile when User is created
    """
    if created:
        try:
            profile = Profile.objects.create(user=instance)
            logger.info(f"✓ Profile created for user: {instance.email}")
            
            # Also create notification settings
            NotificationSettings.objects.create(profile=profile)
            logger.info(f"✓ Notification settings created for user: {instance.email}")
            
        except Exception as e:
            logger.error(f"✗ Failed to create profile for {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Save profile when user is saved (if profile exists)
    """
    if not created and hasattr(instance, 'profile'):
        try:
            instance.profile.save()
        except Exception as e:
            logger.warning(f"Could not save profile for {instance.email}: {str(e)}")