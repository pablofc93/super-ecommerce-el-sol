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
        PedidoItem.objects
        .filter(**filtros)
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
        PedidoItem.objects
        .filter(**filtros)
        .values(
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
# =====================================================
def actualizar_demanda_productos():

    hoy = date.today()

    t = time.perf_counter()
    ProductoMasVendido.objects.all().delete()
    print(f"DELETE: {time.perf_counter()-t:.3f}s")

    t = time.perf_counter()
    resultados = list(calcular_demanda_productos())
    print(f"SELECT: {time.perf_counter()-t:.3f}s")

    t = time.perf_counter()

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

    with transaction.atomic():
        ProductoMasVendido.objects.bulk_create(
            objetos,
            batch_size=500,
        )

    print(f"BULK_CREATE: {time.perf_counter()-t:.3f}s")



# =====================================================
# ACTUALIZAR CATEGORÍAS MÁS MOVIDAS
# =====================================================
def actualizar_categorias_mas_movidas():
    """
    Calcula la demanda histórica por categoría
    utilizando inserción masiva.
    """

    hoy = date.today()

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
# =====================================================
def demanda_por_periodo(periodo="mes"):

    if periodo == "dia":
        fecha_field = "pedido__fecha__date"

    elif periodo == "anio":
        fecha_field = "pedido__fecha__year"

    else:
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
            total_vendido=Sum("cantidad")
        )
        .order_by(fecha_field)
    )


# =====================================================
# PRODUCTOS CON BAJA DEMANDA
# =====================================================
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
        .values(
            "producto_id",
            "producto__nombre",
        )
        .annotate(
            total_vendido=Sum("cantidad")
        )
        .filter(
            total_vendido__lte=min_ventas
        )
        .order_by("total_vendido")
    )