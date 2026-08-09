from django.contrib import admin
from .models import (
    Carrito,
    CarritoItem,
    Pedido,
    PedidoItem,
    Pago
)


# =========================
# CARRITO
# =========================

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Carrito
    """

    list_display = (
        'id',
        'get_cliente',
        'activo',
        'creado_en',
    )

    list_filter = (
        'activo',
        'creado_en',
    )

    search_fields = (
        'cliente__id_cliente__username',
    )

    ordering = (
        '-creado_en',
    )

    def get_cliente(self, obj):
        return obj.cliente.id_cliente.username
    get_cliente.short_description = 'Cliente'


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    """
    Configuración del admin para CarritoItem
    """

    list_display = (
        'carrito',
        'producto',
        'cantidad',
        'precio_unitario',
    )

    list_filter = (
        'producto',
    )

    search_fields = (
        'producto__nombre',
    )


# =========================
# PEDIDO
# =========================

class PedidoItemInline(admin.TabularInline):
    """
    Permite ver y editar los items dentro del pedido
    """
    model = PedidoItem
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Pedido
    """

    list_display = (
        'id_pedido',
        'get_cliente',
        'fecha',
        'estado',
        'total',
    )

    list_filter = (
        'estado',
        'fecha',
    )

    search_fields = (
        'id_pedido',
        'cliente__id_cliente__username',
    )

    ordering = (
        '-fecha',
    )

    readonly_fields = (
        'fecha',
        'total',
    )

    inlines = (
        PedidoItemInline,
    )

    def get_cliente(self, obj):
        return obj.cliente.id_cliente.username
    get_cliente.short_description = 'Cliente'


@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    """
    Admin independiente para PedidoItem (opcional)
    """

    list_display = (
        'pedido',
        'producto',
        'cantidad',
        'precio_unitario',
    )

    list_filter = (
        'producto',
    )


# =========================
# PAGO
# =========================

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Pago
    """

    list_display = (
        'pedido',
        'metodo_pago',
        'monto',
        'estado',
        'fecha_pago',
    )

    list_filter = (
        'metodo_pago',
        'estado',
    )

    search_fields = (
        'pedido__id_pedido',
    )

    ordering = (
        '-fecha_pago',
    )
