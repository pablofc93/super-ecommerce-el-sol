from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del admin para el modelo Usuario personalizado
    """

    # Campos que se muestran en la lista
    list_display = (
        'username',
        'email',
        'tipo_usuario',
        'is_staff',
        'is_active',
        'fecha_registro',
    )

    # Filtros laterales
    list_filter = (
        'tipo_usuario',
        'is_staff',
        'is_active',
    )

    # Búsqueda
    search_fields = (
        'username',
        'email',
    )

    # Orden por defecto
    ordering = ('-fecha_registro',)

    # Campos adicionales al editar
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'tipo_usuario',
                'fecha_registro',
            )
        }),
    )

    # Campos al crear un usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': (
                'email',
                'tipo_usuario',
            )
        }),
    )

    readonly_fields = ('fecha_registro',)
