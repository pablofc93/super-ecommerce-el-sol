from django.urls import path
from .views import (
    DashboardAnaliticoView,
    ProductosMasVendidosView,
    CategoriasMasMovidasAgrupadasView,
    ClientesSegmentadosView,
    ReglasAsociacionView,
    ProductosMasVendidosAgrupadosView,
    DemandaPorMesView,
    VentasPorMesView,
    KpisPorProvinciaView,
    ProductosMasVendidosPublicView,
)

urlpatterns = [
    path('dashboard/', DashboardAnaliticoView.as_view()),

    path('productos-mas-vendidos/', ProductosMasVendidosView.as_view()),
    path('productos-mas-vendidos-agrupados/', ProductosMasVendidosAgrupadosView.as_view()),

    path('categorias-mas-movidas/', CategoriasMasMovidasAgrupadasView.as_view()),

    path('clientes-segmentados/', ClientesSegmentadosView.as_view()),
    path('reglas-asociacion/', ReglasAsociacionView.as_view()),

    path('demanda-mensual/', DemandaPorMesView.as_view()),

    path('ventas-mensuales/', VentasPorMesView.as_view()),

    path('productos-mas-vendidos-public/', ProductosMasVendidosPublicView.as_view()),

    path(
        "kpis-provincia/",
        KpisPorProvinciaView.as_view(),
        name="kpis-provincia",
    ),
]