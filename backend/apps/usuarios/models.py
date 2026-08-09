from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def save(self, *args, **kwargs):
        # Si es admin → marcar como staff automáticamente
        if self.tipo_usuario == 'admin':
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username