from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import CustomerCreate

@receiver(post_save, sender=User)
def set_model_relations(sender , instance , created , **kwargs):
    if created and not hasattr(instance, 'user_registration_form'):
        CustomerCreate.objects.create(
            user=instance,
            username=instance.username,
            email=instance.email or '',
            age=0,
            phone=0,
        )
