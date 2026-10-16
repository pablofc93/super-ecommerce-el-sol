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
    #from datetime import date

    hoy = date.today() # obtener la fecha actual

    # 🔥 LIMPIAR SOLO HOY
    ProductoMasVendido.objects.filter(fecha_calculo=hoy).delete()

    resultados = (
        PedidoItem.objects # modelo que contiene los productos incluidos en los pedidos
        .values('producto_id', 'producto__nombre') # son los campos que se van a obtener de los registros, además se agrupan de acuerdo a estos campos
        .annotate(total_vendido=Sum('cantidad')) # agrega el campo calculado total_vendido, que suma las cantidades de los productos
        .filter(total_vendido__gt=0) # filtra los productos con total_vendido mayor que 0
        .order_by('-total_vendido') # ordener por el campo total_vendido en orden descendente
    )

    # una vez obtenidos los productos más vendidos, se los registra en la tabla de ProductoMasVendido de la bd
    for r in resultados:
        ProductoMasVendido.objects.create(
            producto_id=r['producto_id'], # producto_id almacena el valor de r.producto_id, del producto obtenido en la consulta anterior
            nombre_producto=r['producto__nombre'],
            total_vendido=r['total_vendido'],
            fecha_calculo=hoy
        )


# =====================================================
# CATEGORÍAS MÁS MOVIDAS (categorías de productos que tienen mayores ventas)
# =====================================================
def calcular_categorias_mas_movidas():
    hoy = date.today()

    resultados = (
        PedidoItem.objects
        .filter(pedido__estado__in=['pagado', 'enviado', 'entregado'])
        .values('producto__categoria_id', 'producto__categoria__nombre') # se obtiene el id de la categoria asociada al producto del pedido y el nombre de esa categoria
        .annotate(total_movimiento=Sum('cantidad')) # suma las cantidades de los productos asociado a cada categoria
        .filter(total_movimiento__gt=0) # filtra las categorías que tuvieron un movimiento mayor que 0
        .order_by('-total_movimiento')
    )

    # una vez obtenidas las categorías con mayor movimiento, se las registra en la tabla CategoríaMasMovida de la bd
    for r in resultados:
        CategoriaMasMovida.objects.create(
            categoria_id=r['producto__categoria_id'],
            nombre_categoria=r['producto__categoria__nombre'],
            total_movimiento=r['total_movimiento'],
            fecha_calculo=hoy
        )