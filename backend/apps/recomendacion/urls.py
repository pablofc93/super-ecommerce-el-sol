from django.urls import path

from apps.recomendacion.views import (
    RecomendacionPorClienteView,
    RecomendacionPorCategoriaFavoritaView
)

app_name = "recomendacion"

urlpatterns = [
    # 🔹 Recomendaciones personalizadas por historial del cliente
    path(
        'cliente/<int:id_cliente>/', # url
        RecomendacionPorClienteView.as_view(), # vista asociada a la ruta
        name='recomendacion-por-cliente' # nombre que permite hacer referencia a la ruta en lugar de su url
    ),

    # 🔹 Recomendaciones por categoría favorita del cliente
    path(
        'categoria-favorita/<int:id_cliente>/',
        RecomendacionPorCategoriaFavoritaView.as_view(),
        name='recomendacion-por-categoria-favorita'
    ),
]
