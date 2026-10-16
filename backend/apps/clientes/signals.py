#Este código implementa una señal Django que crea automáticamente un objeto Cliente
#cada vez que se crea un Usuario cuyo tipo_usuario es "cliente"
from django.db.models.signals import post_save #señal de Django
from django.dispatch import receiver #decorador
from django.conf import settings #esto permite acceder a la configuración de Django
from django.apps import apps

from .models import Cliente

#este decorador indica que cuando un usuario se guarda, se ejecuta post_save()
#en ese momento se llama a crear_cliente()
#sender: indica que el modelo que se necesita escuchar es User (usuario)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_cliente(sender, instance, created, **kwargs):
    """
    Crea automáticamente el perfil Cliente
    cuando se registra un Usuario de tipo 'cliente'
    """
    print("Signal ejecutado") #para debuguear
    if created and instance.tipo_usuario == 'cliente':
        Cliente.objects.get_or_create(
            id_cliente=instance #
        )