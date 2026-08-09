from django.contrib import admin
from .models import Admin


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el perfil Admin
    """

    list_display = (
        'get_username',
        'get_email',
        'cargo',
    )

    search_fields = (
        'id_admin__username',
        'id_admin__email',
        'cargo',
    )

    ordering = (
        'id_admin__username',
    )

    fields = (
        'id_admin',
        'cargo',
        'permisos_extra',
    )

    readonly_fields = (
        'id_admin',
    )

    # Métodos auxiliares para mostrar datos del usuario
    def get_username(self, obj):
        return obj.id_admin.username
    get_username.short_description = 'Usuario'

    def get_email(self, obj):
        return obj.id_admin.email
    get_email.short_description = 'Email'
