"""
Comando para generar los productos correspondientes
a cada pedido histórico.

Uso:
    python manage.py seed_pedidoitems

Características:
- Genera PedidoItem.
- Calcula precios históricos.
- Genera canastas realistas agrupando productos.
- Calcula automáticamente el total del pedido.
- No modifica stock.
- No modifica carritos.
- No genera pagos.
- Optimizado para SQLite.
- Utiliza bulk_create().
- Utiliza bulk_update().
"""

from decimal import Decimal
import random
import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.pedidos.models import Pedido, PedidoItem
from apps.productos.models import Producto

from utils.seed.config import (
    DISTRIBUCION_ITEMS_PEDIDO,
    VARIACION_PRECIO_HISTORICO,
    BATCH_SIZE,
)


class Command(BaseCommand):
    help = "Genera los productos correspondientes a cada pedido."

    # =====================================================
    # OBTENER PEDIDOS SIN ITEMS
    # =====================================================
    def obtener_pedidos(self):
        """
        Obtiene únicamente pedidos reales
        que necesitan productos.

        No genera items para pedidos cancelados.
        """
        return list(
            Pedido.objects.filter(
                items__isnull=True,
                estado__in=["pendiente", "pagado", "enviado", "entregado"],
            )
        )

    # =====================================================
    # OBTENER PRODUCTOS
    # =====================================================
    def obtener_productos(self):
        """
        Obtiene todos los productos.

        select_related evita consultas adicionales
        al acceder a la categoría.
        """
        return list(Producto.objects.select_related("categoria").all())

    # =====================================================
    # AGRUPAR PRODUCTOS POR CATEGORÍA
    # =====================================================
    def agrupar_productos_por_categoria(self, productos):
        """
        Agrupa productos según su categoría.

        Ejemplo:
        {
            1: [Producto Aceite, Producto Vinagre],
            2: [Producto Mayonesa, Producto Ketchup]
        }
        """
        categorias = {}
        for producto in productos:
            categoria_id = producto.categoria_id
            if categoria_id not in categorias:
                categorias[categoria_id] = []
            categorias[categoria_id].append(producto)
        return categorias

    # =====================================================
    # POPULARIDAD DE PRODUCTOS
    # =====================================================
    def generar_popularidad(self, productos):
        """
        Asigna pesos de venta.

        Los productos con menor id tendrán
        mayor probabilidad de aparecer.

        Esto permite que algunos productos
        sean más vendidos y genere estadísticas
        más realistas.
        """
        productos = sorted(productos, key=lambda producto: producto.id)
        pesos = {}
        total = len(productos)

        for indice, producto in enumerate(productos):
            porcentaje = indice / total

            if porcentaje < 0.10:
                peso = 20
            elif porcentaje < 0.25:
                peso = 12
            elif porcentaje < 0.50:
                peso = 6
            elif porcentaje < 0.75:
                peso = 3
            else:
                peso = 1

            pesos[producto.id] = peso

        return pesos

    # =====================================================
    # CANTIDAD DE PRODUCTOS DISTINTOS
    # =====================================================
    def cantidad_items_pedido(self):
        """
        Determina cuántos productos distintos
        tendrá cada pedido.

        Usa la distribución definida en config.py.
        """
        return random.choices(
            population=list(DISTRIBUCION_ITEMS_PEDIDO.keys()),
            weights=list(DISTRIBUCION_ITEMS_PEDIDO.values()),
            k=1,
        )[0]

    # =====================================================
    # CANTIDAD DE UNIDADES
    # =====================================================
    def cantidad_unidades(self):
        """
        Determina la cantidad comprada
        de un mismo producto.
        """
        return random.choices(
            population=[1, 2, 3, 4, 5],
            weights=[55, 25, 12, 5, 3],
            k=1,
        )[0]

    # =====================================================
    # PRECIO HISTÓRICO
    # =====================================================
    def calcular_precio_historico(self, producto, fecha_pedido):
        """
        Calcula el precio aproximado que
        tenía el producto en la fecha del pedido.

        Los pedidos antiguos tendrán precios
        menores.
        """
        dias = (timezone.now() - fecha_pedido).days

        if dias <= 180:
            minimo, maximo = VARIACION_PRECIO_HISTORICO["0_180"]
        elif dias <= 365:
            minimo, maximo = VARIACION_PRECIO_HISTORICO["181_365"]
        elif dias <= 730:
            minimo, maximo = VARIACION_PRECIO_HISTORICO["366_730"]
        else:
            minimo, maximo = VARIACION_PRECIO_HISTORICO["731+"]

        factor = Decimal(str(random.uniform(minimo, maximo)))

        return (producto.precio * factor).quantize(Decimal("0.01"))

    # =====================================================
    # SELECCIONAR PRODUCTOS
    # =====================================================
    def seleccionar_productos(self, categorias, pesos, cantidad):
        """
        Genera una canasta realista.

        Regla:
        - 70% aproximadamente de productos
          de una categoría principal.
        - 30% de categorías complementarias.

        Ejemplo:
        Compra:
            Lácteos:
                Leche
                Yogur
                Queso
            Complementos:
                Pan
                Café
        """
        if not categorias:
            return []

        categoria_principal = random.choice(list(categorias.keys()))
        seleccionados = []
        usados = set()

        cantidad_principal = max(
            1, round(cantidad * random.uniform(0.65, 0.80))
        )

        # =================================================
        # PRODUCTOS DE CATEGORÍA PRINCIPAL
        # =================================================
        disponibles = categorias[categoria_principal].copy()

        while disponibles and len(seleccionados) < cantidad_principal:
            pesos_categoria = [pesos[p.id] for p in disponibles]
            indice = random.choices(
                range(len(disponibles)), weights=pesos_categoria, k=1
            )[0]
            producto = disponibles.pop(indice)
            seleccionados.append(producto)
            usados.add(producto.id)

        # =================================================
        # PRODUCTOS COMPLEMENTARIOS
        # =================================================
        categorias_restantes = [
            categoria
            for categoria in categorias.keys()
            if categoria != categoria_principal
        ]
        random.shuffle(categorias_restantes)

        for categoria in categorias_restantes:
            if len(seleccionados) >= cantidad:
                break

            disponibles = categorias[categoria].copy()

            while disponibles and len(seleccionados) < cantidad:
                pesos_categoria = [pesos[p.id] for p in disponibles]
                indice = random.choices(
                    range(len(disponibles)), weights=pesos_categoria, k=1
                )[0]
                producto = disponibles.pop(indice)

                if producto.id in usados:
                    continue

                seleccionados.append(producto)
                usados.add(producto.id)
                break

        return seleccionados

    # =====================================================
    # CREAR ITEMS DEL PEDIDO
    # =====================================================
    def crear_items_pedido(self, pedido, categorias, pesos):
        """
        Genera los PedidoItem correspondientes
        a un pedido.

        Retorna:
        [PedidoItem, PedidoItem, ...]
        y el total calculado.
        """
        items = []
        total = Decimal("0.00")

        cantidad_productos = self.cantidad_items_pedido()

        productos_elegidos = self.seleccionar_productos(
            categorias, pesos, cantidad_productos
        )

        for producto in productos_elegidos:
            cantidad = self.cantidad_unidades()
            precio = self.calcular_precio_historico(producto, pedido.fecha)
            subtotal = precio * cantidad
            total += subtotal

            items.append(
                PedidoItem(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                )
            )

        return items, total

    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================
    def handle(self, *args, **options):
        inicio = time.perf_counter()

        # =================================================
        # OBTENER DATOS BASE
        # =================================================
        pedidos = self.obtener_pedidos()
        productos = self.obtener_productos()

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE ITEMS DE PEDIDO")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Pedidos disponibles  : {len(pedidos)}")
        self.stdout.write(f"Productos disponibles: {len(productos)}")
        self.stdout.write("=" * 60)

        if not pedidos:
            self.stdout.write(
                self.style.SUCCESS("No existen pedidos pendientes de carga.")
            )
            return

        if not productos:
            self.stdout.write(
                self.style.ERROR("No existen productos cargados.")
            )
            return

        # =================================================
        # PREPARAR ESTRUCTURAS
        # =================================================
        self.stdout.write("")
        self.stdout.write("Agrupando productos por categoría...")

        categorias = self.agrupar_productos_por_categoria(productos)

        self.stdout.write(f"Categorías encontradas: {len(categorias)}")

        self.stdout.write("")
        self.stdout.write("Calculando popularidad de productos...")

        pesos = self.generar_popularidad(productos)

        # =================================================
        # GENERAR ITEMS
        # =================================================
        self.stdout.write("")
        self.stdout.write("Generando PedidoItem...")

        items = []
        total_items = 0
        total_importe = Decimal("0.00")

        for pedido in pedidos:
            nuevos_items, total = self.crear_items_pedido(
                pedido, categorias, pesos
            )

            items.extend(nuevos_items)
            pedido.total = total

            total_items += len(nuevos_items)
            total_importe += total

        self.stdout.write("")
        self.stdout.write(f"Items preparados: {len(items)}")

        # =================================================
        # INSERTAR EN SQLITE
        # =================================================
        self.stdout.write("")
        self.stdout.write("Insertando PedidoItem...")

        with transaction.atomic():
            PedidoItem.objects.bulk_create(items, batch_size=BATCH_SIZE)

            self.stdout.write("Actualizando totales de pedidos...")

            Pedido.objects.bulk_update(
                pedidos, ["total"], batch_size=BATCH_SIZE
            )

        fin = time.perf_counter()

        # =================================================
        # ESTADÍSTICAS
        # =================================================
        promedio_items = total_items / len(pedidos) if pedidos else 0
        promedio_importe = (
            total_importe / len(pedidos) if pedidos else Decimal("0.00")
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Items creados correctamente."))

        self.stdout.write("")
        self.stdout.write("Resumen")
        self.stdout.write("-" * 60)
        self.stdout.write(f"Pedidos procesados     : {len(pedidos)}")
        self.stdout.write(f"Items generados        : {total_items}")
        self.stdout.write(f"Promedio items/pedido  : {promedio_items:.2f}")
        self.stdout.write(f"Importe total generado : ${total_importe:,.2f}")
        self.stdout.write(f"Promedio por pedido    : ${promedio_importe:,.2f}")
        self.stdout.write("-" * 60)
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos")
        )