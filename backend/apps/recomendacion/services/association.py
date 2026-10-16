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
    # selecciona las reglas de asociación que sean mayor que la confianza minima, luego las ordena por confianza o lift en orden descendente
    reglas = (
        ReglaAsociacion.objects
        .filter(confianza__gte=confianza_minima)
        .order_by('-confianza', '-lift')
    )

    productos_recomendados = []

     # es un conjunto que permite almacenar datos sin duplicados
     # se utiliza para saber que productos ya fueron agregados
    vistos = set()

    for regla in reglas:
        productos = regla.productos  # ej: [1, 3]

        # comprueba si productos no es realmente una lista o el tamaño de esa lista es menor a 2
        if not isinstance(productos, list) or len(productos) < 2:
            continue

        producto_origen, producto_destino = productos[0], productos[1]

        # La regla aplica solo si el producto base es el origen
        if producto_origen != producto_id:
            continue

        # se coprueba si el producto destino de la regla está en el conjunto de vistos
        # quiere decir si el pructo ya fue recomendado anteriormente, ingorarlo
        if producto_destino in vistos:
            continue

        try:
            producto = Producto.objects.get(id=producto_destino)
        except Producto.DoesNotExist:
            continue

        # finalmente se agrega el pructo recomendado y se registra que ya fue visto
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

    productos_recomendados = [] # se crea la lista de productos recomendados
    vistos = set(productos_ids) # se crea el conjunto de productos ya vistos, o sea, los productos presentes o ya recomendados

    for regla in reglas:
        productos = regla.productos  # ej: [A, B]

        #si productos no es una lista o tiene menos de 2 elementos continúa a la sig regla
        if not isinstance(productos, list) or len(productos) < 2:
            continue

        # separa la regla en producto origen y producto destino
        producto_origen, producto_destino = productos[0], productos[1]

        # se verifica si el p_origen no está dentro de productos_ids (lista de productos del carrito)
        if producto_origen not in productos_ids:
            continue

        # evita recomendar productos que ya están presentes
        if producto_destino in vistos:
            continue

        # busca el producto a recomendar en la bd
        try:
            producto = Producto.objects.get(id=producto_destino)
        except Producto.DoesNotExist:
            continue

        # se encuentra el producto y se agrega a al final de la lista 'productos_recomendados'
        # se agrega también al conjunto de 'vistos'
        productos_recomendados.append(producto)
        vistos.add(producto_destino)

        #se comprueba el límite
        if len(productos_recomendados) >= limite:
            break

    return productos_recomendados
