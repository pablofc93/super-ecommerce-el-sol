# apps/analitica/admin.py

from django.contrib import admin
from .models import (
    ProductoMasVendido,
    CategoriaMasMovida,
    ReglaAsociacion,
    ClienteSegmentado
)

admin.site.register(ProductoMasVendido)
admin.site.register(CategoriaMasMovida)
admin.site.register(ReglaAsociacion)
admin.site.register(ClienteSegmentado)