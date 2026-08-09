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
from itertools import combinations

from apps.pedidos.models import Pedido, PedidoItem
from apps.analitica.models import ReglaAsociacion

import math


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

def calcular_reglas_asociacion(
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
    # Pedidos válidos
    # ------------------------------------------------------
    pedidos_validos = Pedido.objects.filter(
        estado__in=["pagado", "enviado", "entregado"]
    ).values_list("id_pedido", flat=True)

    total_pedidos = pedidos_validos.count()

    print(f"Pedidos válidos: {total_pedidos}")

    if total_pedidos == 0:
        print("No existen pedidos válidos.")
        return []

    # ------------------------------------------------------
    # Construcción de transacciones
    # ------------------------------------------------------
    transacciones = defaultdict(set)

    items = (
        PedidoItem.objects
        .filter(pedido_id__in=pedidos_validos)
        .values("pedido_id", "producto_id")
        .distinct()
    )

    for item in items:
        transacciones[item["pedido_id"]].add(item["producto_id"])

    print(f"Transacciones creadas: {len(transacciones)}")

    # ------------------------------------------------------
    # Conteo individual de productos
    # ------------------------------------------------------
    conteo_productos = defaultdict(int)

    for productos in transacciones.values():
        for producto in productos:
            conteo_productos[producto] += 1

    print(f"Productos distintos encontrados: {len(conteo_productos)}")

    # ------------------------------------------------------
    # Filtrar productos frecuentes (Apriori)
    # ------------------------------------------------------
    frecuencia_minima = max(2,  math.ceil(total_pedidos * soporte_minimo))

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
    # ------------------------------------------------------
    conteo_pares = defaultdict(int)

    for productos in transacciones.values():

        frecuentes = sorted(
            p for p in productos
            if p in productos_frecuentes
        )

        if len(frecuentes) < 2:
            continue

        for par in combinations(frecuentes, 2):
            conteo_pares[par] += 1

    print(f"Pares candidatos: {len(conteo_pares)}")

    # ------------------------------------------------------
    # TOP 20 pares
    # ------------------------------------------------------
    print("\nTOP 20 pares más frecuentes:")

    pares_ordenados = sorted(
        conteo_pares.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if pares_ordenados:
        mejor_par, frecuencia = pares_ordenados[0]
        soporte_real = frecuencia / total_pedidos

        print("\nMEJOR SOPORTE ENCONTRADO")
        print("------------------------")
        print(f"Par: {mejor_par}")
        print(f"Frecuencia: {frecuencia}")
        print(f"Soporte real: {soporte_real:.6f}")
        print(f"Soporte mínimo: {soporte_minimo:.6f}")

    for (a, b), frecuencia in pares_ordenados[:20]:
        print(f"({a}, {b}) -> {frecuencia}")

    # ------------------------------------------------------
    # Calcular reglas
    # ------------------------------------------------------
    reglas = []

    pares_soporte = 0
    pares_confianza = 0
    pares_lift = 0

    descartadas_soporte = 0
    descartadas_confianza = 0
    descartadas_lift = 0

    for (prod_a, prod_b), frecuencia in conteo_pares.items():

        soporte = frecuencia / total_pedidos

        if soporte < soporte_minimo:
            descartadas_soporte += 1
            continue

        pares_soporte += 1

        confianza_ab = frecuencia / conteo_productos[prod_a]
        confianza_ba = frecuencia / conteo_productos[prod_b]

        lift_ab = confianza_ab / (
            conteo_productos[prod_b] / total_pedidos
        )

        lift_ba = confianza_ba / (
            conteo_productos[prod_a] / total_pedidos
        )

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

        if confianza < confianza_minima:
            descartadas_confianza += 1
            continue

        pares_confianza += 1

        if lift < lift_minimo:
            descartadas_lift += 1
            continue

        pares_lift += 1

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
    # Ordenar reglas
    # ------------------------------------------------------
    reglas.sort(
        key=lambda r: (
            r["lift"],
            r["confianza"],
            r["soporte"],
        ),
        reverse=True,
    )

    reglas = reglas[:max_reglas]

    print(f"Reglas finales a guardar: {len(reglas)}")

    # ------------------------------------------------------
    # Guardar reglas
    # ------------------------------------------------------
    reglas_guardadas = []

    for regla in reglas:
        reglas_guardadas.append(
            ReglaAsociacion.objects.create(**regla)
        )

    print("========== FIN APRIORI ==========\n")

    return reglas_guardadas