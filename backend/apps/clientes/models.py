# apps/clientes/models.py
from django.db import models
from apps.usuarios.models import Usuario

#esta clase funciona como perfil complementario del Modelo Usuario
class Cliente(models.Model):

    #relación con Modelo Usuario
    #OneToOneField significa que la relación es 1 a 1
    #quiere decir que un Usuario puede estar asociado solo a un cliente
    #y cada cliente puede estar asociado solo a un usuario
    id_cliente = models.OneToOneField( 
        Usuario,
        on_delete=models.CASCADE, #esto indica que si se elimina un usuario, se elimina el cliente asociado a ese usuario
        primary_key=True, #id_cliente es clave primnaria de clientes
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

    #define la representación textual de un objeto Cliente
    def __str__(self):
        return f"{self.id_cliente.username} - Cliente"