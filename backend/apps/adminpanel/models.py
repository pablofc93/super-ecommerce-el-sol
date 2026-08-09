# apps/adminpanel/models.py
from django.db import models
from apps.usuarios.models import Usuario

class Admin(models.Model):
    id_admin = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='admin'
    )
    cargo = models.CharField(max_length=100)
    permisos_extra = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id_admin.username} - Admin"
