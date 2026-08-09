# apps/clientes/urls.py
from django.urls import path
from .views import (
    home_cliente,
    ClienteProfileView,
    CarritoView,
    CheckoutView,
    HistorialPedidosView,
    DetallePedidoView
)

urlpatterns = [
    path('', home_cliente, name='home-cliente'),
    path('me/', ClienteProfileView.as_view(), name='cliente-profile'),

    # carrito
    path('carrito/', CarritoView.as_view(), name='carrito'),

    # checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # pedidos
    path('pedidos/', HistorialPedidosView.as_view(), name='historial-pedidos'),
    path('pedidos/<int:pedido_id>/', DetallePedidoView.as_view(), name='detalle-pedido'),
]