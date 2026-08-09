from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps

from .models import Cliente


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_cliente(sender, instance, created, **kwargs):
    """
    Crea automáticamente el perfil Cliente
    cuando se registra un Usuario de tipo 'cliente'
    """
    print("Signal ejecutado") #para debuguear
    if created and instance.tipo_usuario == 'cliente':
        Cliente.objects.get_or_create(
            id_cliente=instance
        )