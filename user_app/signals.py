from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import CustomerCreate
from django.db import transaction

@receiver(post_save, sender=User)
def set_model_relations(sender , instance , created , **kwargs):
    """
    Signal to automatically create a CustomerCreate profile
    when a new User is created.
    """
    if created and not hasattr(instance, 'customercreate'):
        with transaction.atomic():
            CustomerCreate.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                age=0,
                phone=0,
            )
