from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.usuarios.models import Usuario
from .models import Admin


@receiver(post_save, sender=Usuario)
def crear_admin(sender, instance, created, **kwargs):
    """
    Crea automáticamente un Admin cuando se registra
    un Usuario de tipo 'admin'
    """
    if created and instance.tipo_usuario == 'admin':
        Admin.objects.create(
            id_admin=instance,
            cargo='Administrador',
            permisos_extra=''
        )
