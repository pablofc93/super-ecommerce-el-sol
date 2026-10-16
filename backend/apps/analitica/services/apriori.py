# apps/analitica/services/apriori.py

"""
Reglas de Asociación (Apriori simplificado)

Objetivo
--------
Detectar productos que suelen comprarse juntos utilizando un algoritmo
basado en Apriori (pares de productos).

Proceso

1. Obtener pedidos válidos
2. Construir transacciones sin productos repetidos
3. Contar frecuencia de cada producto
4. Eliminar productos poco frecuentes (Apriori)
5. Generar pares frecuentes
6. Calcular soporte, confianza y lift
7. Guardar únicamente las mejores reglas
"""

from collections import defaultdict
from itertools import combinations # se utiliza para formar pares entre productos

from apps.pedidos.models import Pedido, PedidoItem
from apps.analitica.models import ReglaAsociacion

import math


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

def calcular_reglas_asociacion(
    # recibe como parámetros estos valores predeterminados
    soporte_minimo=0.001, 
    confianza_minima=0.15,
    lift_minimo=0.80,
    max_reglas=500
):
    """
    Calcula reglas de asociación entre productos y las almacena
    en la tabla ReglaAsociacion.

    Retorna
    -------
    list[ReglaAsociacion]
    """

    print("\n========== APRIORI ==========")

    # ------------------------------------------------------
    # Limpiar reglas anteriores
    # ------------------------------------------------------
    ReglaAsociacion.objects.all().delete()

    # ------------------------------------------------------
    # Pedidos válidos - se obtienen los pedidos cuyos estados son 
    # pagado, enviado o entregado
    # ------------------------------------------------------
    pedidos_validos = Pedido.objects.filter(
        estado__in=["pagado", "enviado", "entregado"]
    ).values_list("id_pedido", flat=True) # se obtiene solamente el campo id_pedido y flat true es para devolver los id como lista de tuplas [(1,),(3,),(5,)]

    total_pedidos = pedidos_validos.count()

    print(f"Pedidos válidos: {total_pedidos}")

    if total_pedidos == 0:
        print("No existen pedidos válidos.")
        return []

    # ------------------------------------------------------
    # Construcción de transacciones
    # ------------------------------------------------------
    transacciones = defaultdict(set)
    # se crea un diccionario especial, la idea es que tenga este formato:
    #{
    #   id_pedido: {id_producto1, id_producto2, etc}
    #}
    # set garantiza que el producto aparezca una sola vez

    items = (
        PedidoItem.objects
        .filter(pedido_id__in=pedidos_validos)
        .values("pedido_id", "producto_id") # solamente se traen estos campos
        .distinct() # elimina los registros duplicados
    )

    for item in items:
        transacciones[item["pedido_id"]].add(item["producto_id"])

    print(f"Transacciones creadas: {len(transacciones)}")

    # ------------------------------------------------------
    # Conteo individual de productos
    # ------------------------------------------------------
    conteo_productos = defaultdict(int)

    # se recorren las transacciones de los pedidos que se construyeron anteriormente 
    # con .values() se obtienen solamente los conjuntos de los productos
    # y dentro 
    for productos in transacciones.values():
        for producto in productos: # se recorren los productos de cada pedido
            conteo_productos[producto] += 1

    print(f"Productos distintos encontrados: {len(conteo_productos)}")

    # ------------------------------------------------------
    # Filtrar productos frecuentes (Apriori)
    # transforma el soporte mínimo porcentual en una cantidad mínima de pedidos
    # ej: si el resultado es 5 significa que el producto tiene que aparecer como mínimo 5 veces
    # ------------------------------------------------------
    frecuencia_minima = max(2,  math.ceil(total_pedidos * soporte_minimo))

    # productos_frecuentes representa un conjunto de elementos (set)
    # se eliminan los productos que aparecen pocas veces
    productos_frecuentes = {
        producto
        for producto, frecuencia in conteo_productos.items()
        if frecuencia >= frecuencia_minima
    }

    print(
        f"Productos frecuentes: {len(productos_frecuentes)} "
        f"(mínimo {frecuencia_minima} apariciones)"
    )

    # ------------------------------------------------------
    # Generación de pares
    # se encarga de generar y contar los pares de productos que aparecen juntos 
    # dentro de los pedidos
    # ------------------------------------------------------

    # diccionario que almacenará cada par de productos que aparecen en una cantidad x de pedidos
    # ej:
    # Producto 1 + Producto 2 → aparecen juntos en 50 pedidos
    # Producto 1 + Producto 5 → aparecen juntos en 30 pedidos
    # Producto 2 + Producto 5 → aparecen juntos en 20 pedidos
    conteo_pares = defaultdict(int) 

    for productos in transacciones.values():

        # aquí se eliminan los productos que fueron considerados poco frecuentes
        # sorted ordena los productos de menor a mayor
        frecuentes = sorted(
            p for p in productos
            if p in productos_frecuentes
        )

        # para crear el par de productos se valida que existan al menos 2 productos
        if len(frecuentes) < 2:
            continue

        # genera las combinaciones posibles de 2 elementos (frecuentes, 2)
        # luego se contabiliza cada par
        for par in combinations(frecuentes, 2):
            conteo_pares[par] += 1

    print(f"Pares candidatos: {len(conteo_pares)}")

    # ------------------------------------------------------
    # TOP 20 pares
    # se ordenan los pares encontrados
    # se identifican los pares más frecuentes
    # se muestran los 20 pares con mayor frecuencia
    # ------------------------------------------------------
    print("\nTOP 20 pares más frecuentes:")

    # se ordenan los pares de acuerdo a la frecuencia
    pares_ordenados = sorted(
        conteo_pares.items(),
        # esta parte indica que para ordenar 
        # los pares se utiliza el segundo valor 
        # de los pares, es decir, 
        # la cantidad pedidos en los que aparecen los pares
        key=lambda x: x[1], 
        reverse=True # indica que se deben ordenar de mayor a menor
    )

    # se obtienen los pares ordenados del mas al menos frecuente
    if pares_ordenados:
        mejor_par, frecuencia = pares_ordenados[0]
        soporte_real = frecuencia / total_pedidos # se calcula el soporte real del mejor par

        print("\nMEJOR SOPORTE ENCONTRADO")
        print("------------------------")
        print(f"Par: {mejor_par}")
        print(f"Frecuencia: {frecuencia}")
        print(f"Soporte real: {soporte_real:.6f}")
        print(f"Soporte mínimo: {soporte_minimo:.6f}")

    # aquí se muestran los 20 pares mas frecuentes
    for (a, b), frecuencia in pares_ordenados[:20]:
        print(f"({a}, {b}) -> {frecuencia}")

    # ------------------------------------------------------
    # Calcular reglas
    # ------------------------------------------------------
    reglas = [] # se crea la lista de reglas

    # contadores usados para estadísticas del algoritmo
    pares_soporte = 0   
    pares_confianza = 0
    pares_lift = 0

    # contadores de pares descartados
    # sirven para saber por qué fueron descontados los pares
    descartadas_soporte = 0
    descartadas_confianza = 0
    descartadas_lift = 0

    for (prod_a, prod_b), frecuencia in conteo_pares.items():

        soporte = frecuencia / total_pedidos # por cada tupla desempaquetada se calcula el soporte

        if soporte < soporte_minimo:
            descartadas_soporte += 1
            continue

        pares_soporte += 1

        # se calcula la confianza en ambos sentidos del par
        confianza_ab = frecuencia / conteo_productos[prod_a] # frecuencia(A,B) / frecuencia(A)
        confianza_ba = frecuencia / conteo_productos[prod_b]

        # se calcula el lift en ambos sentidos del par
        lift_ab = confianza_ab / (
            conteo_productos[prod_b] / total_pedidos
        )

        lift_ba = confianza_ba / (
            conteo_productos[prod_a] / total_pedidos
        )

        # se elige la dirección de la regla
        if confianza_ab >= confianza_ba:
            origen = prod_a
            destino = prod_b
            confianza = confianza_ab
            lift = lift_ab
        else:
            origen = prod_b
            destino = prod_a
            confianza = confianza_ba
            lift = lift_ba

        # segundo filtro: si la confianza obtenida es menor que la confianza mínima establecida, se descarta
        if confianza < confianza_minima:
            descartadas_confianza += 1
            continue

        pares_confianza += 1

        # tercer filtro: si el lift obtenido es menor que el lift mínimo establecido, se descarta
        if lift < lift_minimo:
            descartadas_lift += 1
            continue

        pares_lift += 1

        # las reglas que pasaron todos los filtros se agregan a la lista de reglas
        reglas.append({
            "productos": [origen, destino],
            "soporte": round(soporte, 4),
            "confianza": round(confianza, 4),
            "lift": round(lift, 4),
        })

    # ------------------------------------------------------
    # Estadísticas
    # ------------------------------------------------------
    print("\n========== ESTADÍSTICAS APRIORI ==========")
    print(f"Pedidos válidos: {total_pedidos}")
    print(f"Transacciones: {len(transacciones)}")
    print(f"Productos únicos: {len(conteo_productos)}")
    print(f"Pares distintos encontrados: {len(conteo_pares)}")
    print(f"Pares que pasan soporte: {pares_soporte}")
    print(f"Pares que pasan confianza: {pares_confianza}")
    print(f"Pares que pasan lift: {pares_lift}")
    print(f"Descartadas por soporte: {descartadas_soporte}")
    print(f"Descartadas por confianza: {descartadas_confianza}")
    print(f"Descartadas por lift: {descartadas_lift}")
    print("=========================================\n")

    # ------------------------------------------------------
    # Ordenar reglas según sus métricas
    # ------------------------------------------------------
    reglas.sort(
        key=lambda r: (
            r["lift"],
            r["confianza"],
            r["soporte"],
        ),
        reverse=True, # orden descendente
    )

    reglas = reglas[:max_reglas]

    print(f"Reglas finales a guardar: {len(reglas)}")

    # ------------------------------------------------------
    # Guardar reglas
    # ------------------------------------------------------
    reglas_guardadas = []

    for regla in reglas:
        reglas_guardadas.append(
            ReglaAsociacion.objects.create(**regla) # inserta las reglas generadas en la base de datos, en la tabla ReglaAsociacion
        )

    print("========== FIN APRIORI ==========\n")

    return reglas_guardadas