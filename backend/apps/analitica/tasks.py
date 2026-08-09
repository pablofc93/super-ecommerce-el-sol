from datetime import date
from django.db.models import Sum

from apps.analitica.models import (
    ProductoMasVendido,
    CategoriaMasMovida
)

from apps.pedidos.models import PedidoItem


# =====================================================
# LIMPIEZA DE DATOS
# =====================================================
def limpiar_datos():
    """
    Limpia TODOS los registros analíticos.
    Esto asegura que siempre trabajamos con snapshot actual.
    """
    ProductoMasVendido.objects.all().delete()
    CategoriaMasMovida.objects.all().delete()


# =====================================================
# PRODUCTOS MÁS VENDIDOS
# =====================================================
def calcular_productos_mas_vendidos():
    from datetime import date

    hoy = date.today()

    # 🔥 LIMPIAR SOLO HOY
    ProductoMasVendido.objects.filter(fecha_calculo=hoy).delete()

    resultados = (
        PedidoItem.objects
        .values('producto_id', 'producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .filter(total_vendido__gt=0)
        .order_by('-total_vendido')
    )

    for r in resultados:
        ProductoMasVendido.objects.create(
            producto_id=r['producto_id'],
            nombre_producto=r['producto__nombre'],
            total_vendido=r['total_vendido'],
            fecha_calculo=hoy
        )


# =====================================================
# CATEGORÍAS MÁS MOVIDAS
# =====================================================
def calcular_categorias_mas_movidas():
    hoy = date.today()

    resultados = (
        PedidoItem.objects
        .filter(pedido__estado__in=['pagado', 'enviado', 'entregado'])
        .values('producto__categoria_id', 'producto__categoria__nombre')
        .annotate(total_movimiento=Sum('cantidad'))
        .filter(total_movimiento__gt=0)
        .order_by('-total_movimiento')
    )

    for r in resultados:
        CategoriaMasMovida.objects.create(
            categoria_id=r['producto__categoria_id'],
            nombre_categoria=r['producto__categoria__nombre'],
            total_movimiento=r['total_movimiento'],
            fecha_calculo=hoy
        )