"""
Configuración utilizada por todos los comandos de generación
de datos (seed) del proyecto.
"""

# =========================================================
# CARRITOS
# =========================================================

# Porcentaje de carritos que permanecerán activos
PORCENTAJE_CARRITOS_ACTIVOS = 0.75

# Porcentaje de carritos que contendrán productos
PORCENTAJE_CARRITOS_CON_ITEMS = 0.70


# =========================================================
# PEDIDOS
# =========================================================

# Porcentaje de clientes (con carrito e items)
# que tendrán al menos un pedido.
PORCENTAJE_CLIENTES_CON_PEDIDOS = 0.60

# Cantidad de pedidos que puede tener un mismo cliente.
PEDIDOS_MINIMOS_POR_CLIENTE = 1
PEDIDOS_MAXIMOS_POR_CLIENTE = 8

# Antigüedad máxima de los pedidos históricos.
# Ejemplo:
# 2 = desde hace dos años hasta hoy.
ANIOS_HISTORICOS_PEDIDOS = 2

# Distribución de estados de los pedidos.
#
# Debe sumar 100.
#
# Se utilizará con random.choices()
# para generar estados realistas.
ESTADOS_PEDIDO = {
    "entregado": 65,
    "enviado": 15,
    "pagado": 10,
    "pendiente": 5,
    "cancelado": 5,
}


# =========================================================
# PAGOS
# =========================================================

PORCENTAJE_PAGOS_APROBADOS = 0.95

PORCENTAJE_PAGOS_RECHAZADOS = 0.03

PORCENTAJE_PAGOS_PENDIENTES = 0.02


# =========================================================
# CARRITO ITEMS
# =========================================================

PRODUCTOS_MINIMOS_POR_CARRITO = 1

PRODUCTOS_MAXIMOS_POR_CARRITO = 12


# =========================================================
# PEDIDO ITEMS
# =========================================================

# Cantidad de productos distintos por pedido.
#
# La suma de los pesos no necesita ser 100.
# Se utiliza con random.choices().
#
# Esto genera una distribución similar a un supermercado.

# Cantidad de PRODUCTOS DISTINTOS por pedido.
# No representa la cantidad de unidades.
DISTRIBUCION_ITEMS_PEDIDO = {

    1: 18,

    2: 22,

    3: 20,

    4: 15,

    5: 10,

    6: 7,

    7: 4,

    8: 2,

    9: 1,

    10: 1,

}

BATCH_SIZE = 500

# =========================================================
# PRECIOS HISTÓRICOS
# =========================================================

VARIACION_PRECIO_HISTORICO = {

    "0_180": (0.97, 1.00),

    "181_365": (0.90, 0.97),

    "366_730": (0.75, 0.90),

    "731+": (0.60, 0.75),

}


# =========================================================
# CANTIDADES
# =========================================================

CANTIDAD_MINIMA_PRODUCTO = 1

CANTIDAD_MAXIMA_PRODUCTO = 5