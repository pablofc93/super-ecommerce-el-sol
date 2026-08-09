"""
Servicios de recomendación basados en reglas de asociación (Apriori).

Este módulo:
- Consume las reglas ya calculadas en analitica.ReglaAsociacion
- No recalcula métricas
- Interpreta correctamente el campo JSON 'productos'
"""

from apps.analitica.models import ReglaAsociacion
from apps.productos.models import Producto


def recomendar_por_producto(producto_id, limite=5, confianza_minima=0.0):
    """
    Recomienda productos a partir de un producto base.

    La regla se interpreta como:
    productos = [producto_origen, producto_destino]

    Args:
        producto_id (int): producto que el cliente está viendo
        limite (int): cantidad máxima de recomendaciones
        confianza_minima (float): filtro mínimo de confianza

    Returns:
        list[Producto]
    """

    reglas = (
        ReglaAsociacion.objects
        .filter(confianza__gte=confianza_minima)
        .order_by('-confianza', '-lift')
    )

    productos_recomendados = []
    vistos = set()

    for regla in reglas:
        productos = regla.productos  # ej: [1, 3]

        if not isinstance(productos, list) or len(productos) < 2:
            continue

        producto_origen, producto_destino = productos[0], productos[1]

        # La regla aplica solo si el producto base es el origen
        if producto_origen != producto_id:
            continue

        if producto_destino in vistos:
            continue

        try:
            producto = Producto.objects.get(id=producto_destino)
        except Producto.DoesNotExist:
            continue

        productos_recomendados.append(producto)
        vistos.add(producto_destino)

        if len(productos_recomendados) >= limite:
            break

    return productos_recomendados


def recomendar_por_lista_productos(productos_ids, limite=5):
    """
    Recomienda productos a partir de múltiples productos (ej: carrito).

    Args:
        productos_ids (list[int]): productos presentes en el carrito
        limite (int): máximo de recomendaciones

    Returns:
        list[Producto]
    """

    reglas = (
        ReglaAsociacion.objects
        .order_by('-confianza', '-lift')
    )

    productos_recomendados = []
    vistos = set(productos_ids)

    for regla in reglas:
        productos = regla.productos  # ej: [A, B]

        if not isinstance(productos, list) or len(productos) < 2:
            continue

        producto_origen, producto_destino = productos[0], productos[1]

        if producto_origen not in productos_ids:
            continue

        if producto_destino in vistos:
            continue

        try:
            producto = Producto.objects.get(id=producto_destino)
        except Producto.DoesNotExist:
            continue

        productos_recomendados.append(producto)
        vistos.add(producto_destino)

        if len(productos_recomendados) >= limite:
            break

    return productos_recomendados
