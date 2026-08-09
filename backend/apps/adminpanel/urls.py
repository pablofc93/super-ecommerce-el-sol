from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),

    # Autenticación admin
    path('login/', views.login_admin, name='admin_login'),

    # Gestión de productos
    path('productos/', views.admin_productos_lista, name='admin_productos'),
    path('productos/agregar/', views.admin_productos_agregar, name='admin_producto_agregar'),
    path('productos/<int:id>/editar/', views.admin_productos_editar, name='admin_producto_editar'),

    # Gestión de usuarios
    path('usuarios/', views.admin_usuarios_lista, name='admin_usuarios'),
    path('usuarios/agregar/', views.admin_usuarios_agregar, name='admin_usuario_agregar'),
    path('usuarios/<int:id>/editar/', views.admin_usuarios_editar, name='admin_usuario_editar'),

    # Gestión de pedidos
    path('pedidos/', views.admin_pedidos_lista, name='admin_pedidos'),
    path('pedidos/<int:id>/', views.admin_pedido_detalle, name='admin_pedido_detalle'),

    # Perfil admin
    path('perfil/', views.admin_perfil, name='admin_perfil'),

    # Reportes
    path('reportes/', views.admin_reportes, name='admin_reportes'),
]
