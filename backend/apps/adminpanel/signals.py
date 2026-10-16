from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.usuarios.models import Usuario
from .models import Admin

# este decorador indica que la función crear_admin se ejecutará después de que se guarde un objeto Usuario en la base de datos
#post_save es una señal que se envía después de que un modelo se guarda en la base de datos.
# sender indica que la señal se enviará solo cuando se guarde un objeto del modelo Usuario.
# insrance es el objeto Usuario que se acaba de guardar.
# created es un booleano que indica si el objeto Usuario se acaba de crear (True) o si se está actualizando (False).
@receiver(post_save, sender=Usuario)
def crear_admin(sender, instance, created, **kwargs):
    """
    Crea automáticamente un Admin cuando se registra
    un Usuario de tipo 'admin'
    """
    if created and instance.tipo_usuario == 'admin':
        Admin.objects.create(
            id_admin=instance, #relaciona el objeto Admin con el objeto Usuario recién creado, no recibe un id sino el objeto completo.
            cargo='Administrador',
            permisos_extra=''
        )
