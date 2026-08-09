from django.urls import path

from .views import (
    DashboardView,
    IngresosPorClienteView,
    ReportesHistoricosView,
    RegistrarAccesoView
)

urlpatterns = [

    path(
        'dashboard/',
        DashboardView.as_view()
    ),

    path(
        'ingresos-clientes/',
        IngresosPorClienteView.as_view()
    ),

    path(
        'historicos/',
        ReportesHistoricosView.as_view()
    ),

    # 🔥 NUEVO
    path(
        'registrar-acceso/',
        RegistrarAccesoView.as_view()
    ),

]