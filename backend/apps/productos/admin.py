from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, Producto, Compra


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "precio",
        "stock",
        "creado_en",
        "imagen_preview",  # 👈 vista previa
    )
    list_filter = ("categoria",)
    search_fields = ("nombre",)
    readonly_fields = ("imagen_preview",)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 80px; height: auto; border-radius: 6px;" />',
                obj.imagen.url
            )
        return "Sin imagen"

    imagen_preview.short_description = "Imagen"


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("cliente", "producto", "cantidad", "fecha")
    list_filter = ("fecha", "producto")
    search_fields = (
        "cliente__user__username",
        "producto__nombre",
    )
