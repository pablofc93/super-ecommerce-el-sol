#admin.py sirve para verificar rápido que todo anda bien
# aquí se configura como se va a mostar y administrar el modelo ReporteHistorico
# dentro del panel de administración de Django
from django.contrib import admin
from .models import ReporteHistorico


@admin.register(ReporteHistorico)
class ReporteHistoricoAdmin(admin.ModelAdmin):
    list_display = ( # tupla que indica las columnas visibles en el listado del panel de admin de Django
        'id',
        'tipo',
        'fecha_generacion',
        'generado_por',
    )
    list_filter = ('tipo', 'fecha_generacion') # campos utilizados para filtrar
    search_fields = ('tipo',) # camops utilizados para buscar
    readonly_fields = ('fecha_generacion',) # campos de solo lectura
