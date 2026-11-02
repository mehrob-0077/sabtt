from django.db.models.signals import post_save
from django.dispatch import receiver

from .helpers import send_confirmation_email
from .models import CostumUser, EmailConfirmed


@receiver(post_save, sender=CostumUser)
def create_email_confirmation(sender, instance, created, **kwargs):
    """Create and send an email confirmation link for a newly registered user."""
    if not created:
        return

    instance.is_active = False
    instance.save(update_fields=['is_active'])
    confirmation = EmailConfirmed.objects.create(user=instance)
    send_confirmation_email(confirmation)
