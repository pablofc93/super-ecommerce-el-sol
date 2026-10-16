"""
Servicio de análisis de demanda de productos.

Responsabilidades:
- Analizar ventas históricas
- Calcular demanda por producto y categoría
- Preparar datos para analítica y predicción futura

Este archivo NO expone endpoints
NO toca serializers
NO maneja permisos

Es lógica de negocio pura.
"""

from datetime import date

from django.db import transaction
from django.db.models import Sum, Count

from apps.pedidos.models import PedidoItem
from apps.analitica.models import (
    ProductoMasVendido,
    CategoriaMasMovida,
)

import time
from django.db import transaction


# =====================================================
# DEMANDA GENERAL POR PRODUCTO
# =====================================================
def calcular_demanda_productos(fecha_inicio=None, fecha_fin=None):

    # se crea un diccionario de filtros que contiene las condiciones que deberían cumplir los registros
    # obtenidos de la base de datos para ser considerados en el cálculo de la demanda por producto
    filtros = {
        "pedido__estado__in": [
            "pagado",
            "enviado",
            "entregado",
        ]
    }

    # estas condiciones comprueban si se han proporcionado fechas de inicio y fin para filtrar los registros por fecha
    if fecha_inicio:
        filtros["pedido__fecha__date__gte"] = fecha_inicio

    if fecha_fin:
        filtros["pedido__fecha__date__lte"] = fecha_fin

    return (
        PedidoItem.objects
        .filter(**filtros) # ** permite covertir el diccionario en argumentos nombrados para .filter()
        .values(
            "producto_id",
            "producto__nombre",
        )
        .annotate(
            total_vendido=Sum("cantidad"),
            veces_comprado=Count("pedido_id"),
        )
        .order_by("-total_vendido")
    )


# =====================================================
# DEMANDA GENERAL POR CATEGORÍA
# =====================================================
def calcular_demanda_categorias(fecha_inicio=None, fecha_fin=None):

    # se filtran los registros de PedidoItem según el estado del pedido y las fechas proporcionadas, si las hay.
    filtros = {
        "pedido__estado__in": [
            "pagado",
            "enviado",
            "entregado",
        ]
    }

    if fecha_inicio:
        filtros["pedido__fecha__date__gte"] = fecha_inicio

    if fecha_fin:
        filtros["pedido__fecha__date__lte"] = fecha_fin

    return (
        PedidoItem.objects # PedidoItem representa los productos incluidos dentro de los pedidos
        .filter(**filtros) # se aplican los filtros definidos previamente. ** permite pasar el diccionario como argumentos al método .filter()
        .values( # agrupa por categoría
            "producto__categoria_id",
            "producto__categoria__nombre",
        )
        .annotate(
            total_movimiento=Sum("cantidad")
        )
        .order_by("-total_movimiento")
    )


# =====================================================
# ACTUALIZAR PRODUCTOS MÁS VENDIDOS
#
# recalcula y actualiza la tabla de ProductoMasVendido
# utilizando las ventas históricas actuales
# =====================================================
def actualizar_demanda_productos():

    # obtener la fecha de cálculo
    hoy = date.today() 

    #eliminar los resultados anteriores
    t = time.perf_counter() # se guarda el instante de inicio de la operación
    ProductoMasVendido.objects.all().delete() # elimina los registros existentes
    print(f"DELETE: {time.perf_counter()-t:.3f}s") # muestra el tiempo de la operación delete

    # 
    t = time.perf_counter()
    resultados = list(calcular_demanda_productos()) # se obtiene una lista con los resultados de la demanda por productos
    print(f"SELECT: {time.perf_counter()-t:.3f}s") # se muestra el tiempo de la operación para calcular

    t = time.perf_counter()

    # se crean los objetos de los productos más vendidos para posteriormente almacenarlos en la bd
    # estos objetos se crean todos en memoria y luego se los almacena de una sola vez
    objetos = [
        ProductoMasVendido(
            producto_id=r["producto_id"],
            nombre_producto=r["producto__nombre"],
            total_vendido=r["total_vendido"],
            fecha_calculo=hoy,
        )
        for r in resultados
    ]

    print(f"OBJETOS: {time.perf_counter()-t:.3f}s")

    t = time.perf_counter()

    # se insertan todos los productos mediante una única consulta
    # esta única consulta es una transacción atómica
    with transaction.atomic():
        ProductoMasVendido.objects.bulk_create(
            objetos,
            batch_size=500,
        )

    print(f"BULK_CREATE: {time.perf_counter()-t:.3f}s")



# =====================================================
# ACTUALIZAR CATEGORÍAS MÁS MOVIDAS
# recalcula y actualiza en la base de datos las categorías que tienen mayor movimiento/venta histórica
# =====================================================
def actualizar_categorias_mas_movidas():
    """
    Calcula la demanda histórica por categoría
    utilizando inserción masiva.
    """

    hoy = date.today()

    # se llama la a la funcion calcular_demanda_categorias() 
    # que se encarga de realizar todo el cálculo correspondiente
    resultados = list(calcular_demanda_categorias()) 

    objetos = [
        CategoriaMasMovida(
            categoria_id=r["producto__categoria_id"],
            nombre_categoria=r["producto__categoria__nombre"],
            total_movimiento=r["total_movimiento"],
            fecha_calculo=hoy,
        )
        for r in resultados
    ]

    with transaction.atomic():

        CategoriaMasMovida.objects.all().delete()

        CategoriaMasMovida.objects.bulk_create(
            objetos,
            batch_size=500,
        )


# =====================================================
# DEMANDA POR PERÍODO
# calcula cuántas unidades de productos se vendieron
# agrupadas por un período de tiempo
# =====================================================
def demanda_por_periodo(periodo="mes"): # este método recibe como parámetro un perioodo predeterminado denominado "mes"

    if periodo == "dia": # si se agrupa por día, se utiliza la fecha completa
        fecha_field = "pedido__fecha__date"

    elif periodo == "anio": # si se agrupa por año, se extrañe el año de la fecha
        fecha_field = "pedido__fecha__year"

    else: # si se agrupa por mes, se extrae el mes de la fecha
        fecha_field = "pedido__fecha__month"

    return (
        PedidoItem.objects
        .filter(
            pedido__estado__in=[
                "pagado",
                "enviado",
                "entregado",
            ]
        )
        .values(fecha_field)
        .annotate(
            total_vendido=Sum("cantidad") # cantidad representa la cantidad de unidades que contiene cada PedidoItem.
        )
        .order_by(fecha_field)
    )


# =====================================================
# PRODUCTOS CON BAJA DEMANDA
# =====================================================

# el parámetro min_ventas indica que el máximo de unidades vendidas que debe tener
# un producto para ser considerado de baja demanda es 5
def productos_baja_demanda(min_ventas=5):

    return (
        PedidoItem.objects
        .filter(
            pedido__estado__in=[
                "pagado",
                "enviado",
                "entregado",
            ]
        )
        .values( # agrupa por nombre de producto
            "producto_id",
            "producto__nombre",
        )
        .annotate(
            total_vendido=Sum("cantidad")
        )
        .filter( #filtra los productos cuyo total vendido sea menor o igual al limite establecido
            total_vendido__lte=min_ventas
        )
        .order_by("total_vendido")
    )