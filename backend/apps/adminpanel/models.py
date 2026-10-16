# apps/adminpanel/models.py
from django.db import models
from apps.usuarios.models import Usuario

# se crea una clase llamada Admin que hereda de models.Model
# por lo tanto, se crea una tabla en la base de datos para almacenar información sobre los administradores del sistema.
class Admin(models.Model):
    id_admin = models.OneToOneField(
        Usuario, #relación con usuario -> indica que solo un usuario puede ser un administrador y viceversa.
        on_delete=models.CASCADE,
        primary_key=True, #indica que id_admin será la clave primaria de la tabla Admin.
        related_name='admin' #se define el nombre que se utilizará para acceder a Admin desde un objeto Usuario
    )
    cargo = models.CharField(max_length=100)
    permisos_extra = models.TextField(blank=True, null=True)

    # este método define cómo se mostrará el objeto Admin cuando Django necesite 
    # representarlo como una cadena de texto, por ejemplo, en el panel de administración.
    def __str__(self):
        return f"{self.id_admin.username} - Admin"
