# apps/clientes/models.py
from django.db import models
from apps.usuarios.models import Usuario


class Cliente(models.Model):

    id_cliente = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cliente'
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    direccion = models.CharField(
        max_length=255,
        blank=True
    )

    ciudad = models.CharField(
        max_length=100,
        blank=True
    )

    provincia = models.CharField(
        max_length=100,
        blank=True
    )

    codigo_postal = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return f"{self.id_cliente.username} - Cliente"