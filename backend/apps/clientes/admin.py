from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Cliente
    """

    # Columnas visibles en la lista
    list_display = (
        'get_username',
        'get_email',
        'telefono',
        'ciudad',
        'provincia',
        'codigo_postal',
    )

    # Filtros laterales
    list_filter = (
        'ciudad',
        'provincia',
    )

    # Búsqueda
    search_fields = (
        'id_cliente__username',
        'id_cliente__email',
        'telefono',
        'ciudad',
        'provincia',
    )

    # Orden por defecto
    ordering = (
        'id_cliente__username',
    )

    # Campos del formulario
    fields = (
        'id_cliente',
        'telefono',
        'direccion',
        'ciudad',
        'provincia',
        'codigo_postal',
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('id_cliente',)
        return ()

    # Métodos auxiliares para mostrar datos del usuario
    def get_username(self, obj):
        return obj.id_cliente.username
    get_username.short_description = 'Usuario'

    def get_email(self, obj):
        return obj.id_cliente.email
    get_email.short_description = 'Email'