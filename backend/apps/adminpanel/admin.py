from django.contrib import admin # importa el modulo de administración de Django
from .models import Admin # importa el modelo Admin definido en el archivo models.py del mismo directorio

#este decorador registra el modelo Admin en el panel de administración de Django, utilizando la clase AdminAdmin para definir su configuración.
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el perfil Admin
    """

    # determina qué campos se mostrarán en la lista de objetos Admin en el panel de administración.
    list_display = (
        'get_username',
        'get_email',
        'cargo',
    )

    # determina qué campos se pueden buscar en la lista de objetos Admin en el panel de administración.
    search_fields = (
        'id_admin__username',
        'id_admin__email',
        'cargo',
    )

    # ordena los objetos Admin en la lista de objetos del panel de administración según el nombre de usuario del usuario relacionado.
    ordering = (
        'id_admin__username',
    )

    # determina qué campos se mostrarán en el formulario de edición de un objeto Admin en el panel de administración.
    fields = (
        'id_admin',
        'cargo',
        'permisos_extra',
    )

    # determina qué campos serán de solo lectura en el formulario de edición de un objeto Admin en el panel de administración.
    readonly_fields = (
        'id_admin',
    )

    # Métodos auxiliares para mostrar datos del usuario

    #devuelve el nombre de usuario del usuario relacionado con el objeto Admin.
    #get_username indica que se utilice 'Usuario' como nombre de la columna en la lista de objetos Admin en el panel de administración.
    def get_username(self, obj):
        return obj.id_admin.username
    get_username.short_description = 'Usuario'

    def get_email(self, obj):
        return obj.id_admin.email
    get_email.short_description = 'Email'
