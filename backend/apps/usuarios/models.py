from django.contrib.auth.models import AbstractUser
from django.db import models

#se crea la calse Usuario que hereda de la clase existente AbstractUser de Django, 
# que ya tiene los campos username, 
# password, first_name, last_name, is_staff, is_active y date_joined
class Usuario(AbstractUser): 
    TIPO_USUARIO_CHOICES = (
        ('cliente', 'Cliente'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    #self representa la instancia actual del modelo Usuario.
    #si el tipo de usuario es admin, se marca automáticamente como staff
    #super() llama al método save() de la clase base (AbstractUser) para guardar la instancia en la base de datos.
    def save(self, *args, **kwargs):
        # Si es admin → marcar como staff automáticamente
        if self.tipo_usuario == 'admin':
            self.is_staff = True
        super().save(*args, **kwargs)

    #este método sirve para mostrar el objeto texto, ejemplo nuevo usuario creado = 'pablo123'
    def __str__(self):
        return self.username