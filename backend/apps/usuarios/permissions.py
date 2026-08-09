from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Permite acceso solo a usuarios con tipo_usuario = 'admin'
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.tipo_usuario == 'admin'
        )