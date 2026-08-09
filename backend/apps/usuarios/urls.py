from django.urls import path
from .views import ChangePasswordView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    get_csrf,
    AdminListarUsuariosView,
    AdminCrearUsuarioView,
    AdminCambiarRolView,
    AdminEliminarUsuarioView
)

urlpatterns = [
    path('csrf/', get_csrf, name='csrf'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),

    # 🔥 ADMIN
    path('admin/listar/', AdminListarUsuariosView.as_view()),
    path('admin/crear/', AdminCrearUsuarioView.as_view()),
    path('admin/<int:user_id>/rol/', AdminCambiarRolView.as_view()),
    path('admin/<int:user_id>/eliminar/', AdminEliminarUsuarioView.as_view()),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]