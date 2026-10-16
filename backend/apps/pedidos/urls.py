from django.urls import path
from .views import (
    CarritoView,
    AgregarProductoCarritoView,
    EliminarProductoCarritoView,
    VaciarCarritoView,
    ConfirmarPedidoView,
    ListarPedidosView,
    CancelarPedidoView,
    AdminListarPedidosView,
    AdminCambiarEstadoPedidoView,
    AdminDetallePedidoView,
    AdminPedidosPorEstadoView
)

urlpatterns = [ #urlpatterns es una lista especial de Django para definir rutas que se definen para la aplicación de pedidos
    path('carrito/', CarritoView.as_view()),
    path('carrito/agregar/', AgregarProductoCarritoView.as_view()),
    path('carrito/eliminar/item/<int:item_id>/', EliminarProductoCarritoView.as_view()),
    path('carrito/vaciar/', VaciarCarritoView.as_view()),
    path('confirmar/', ConfirmarPedidoView.as_view()),
    path('listar/', ListarPedidosView.as_view()), #para listar pedidos del cliente autenticado
    path('cancelar/<int:pedido_id>/', CancelarPedidoView.as_view()),

    # ADMIN
    path('admin/listar/', AdminListarPedidosView.as_view()),
    path('admin/<int:pedido_id>/estado/', AdminCambiarEstadoPedidoView.as_view()),
    path('admin/<int:pedido_id>/', AdminDetallePedidoView.as_view()),
    path('admin/por-estado/', AdminPedidosPorEstadoView.as_view()), #buscar pedidos por estado, para el dashboard del admin
]