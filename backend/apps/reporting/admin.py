#admin.py sirve para verificar rápido que todo anda bien
from django.contrib import admin
from .models import ReporteHistorico


@admin.register(ReporteHistorico)
class ReporteHistoricoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tipo',
        'fecha_generacion',
        'generado_por',
    )
    list_filter = ('tipo', 'fecha_generacion')
    search_fields = ('tipo',)
    readonly_fields = ('fecha_generacion',)
