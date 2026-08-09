"""
Comando para generar el historial de compras de los clientes.

Uso:

python manage.py seed_compras

Características

- Genera una Compra por cada PedidoItem válido.
- Solo procesa pedidos:
    * entregado
    * enviado
    * pagado
- Conserva la fecha histórica del pedido.
- Conserva la cantidad comprada.
- No modifica stock.
- No modifica pedidos.
- No modifica pagos.
- Evita compras duplicadas.
- Utiliza bulk_create().
"""

import time

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.productos.models import Compra
from apps.pedidos.models import PedidoItem


class Command(BaseCommand):
    help = "Genera el historial de compras desde PedidoItem."

    # =====================================================
    # PEDIDOS VÁLIDOS
    # =====================================================

    def obtener_items_validos(self):
        """
        Devuelve únicamente los PedidoItem cuyo
        pedido representa una compra realizada.
        """
        return (
            PedidoItem.objects.select_related(
                "pedido", "pedido__cliente", "producto"
            ).filter(
                pedido__estado__in=["entregado", "enviado", "pagado"]
            )
        )

    # =====================================================
    # COMPRAS YA EXISTENTES
    # =====================================================

    def obtener_items_ya_procesados(self):
        """
        Devuelve un conjunto con los ids de PedidoItem
        que ya poseen una Compra asociada.

        Esto permite ejecutar el comando
        varias veces sin duplicar datos.
        """
        return set(
            Compra.objects.exclude(pedido_item__isnull=True).values_list(
                "pedido_item_id", flat=True
            )
        )

    # =====================================================
    # CREAR COMPRA
    # =====================================================

    def crear_compra(self, item):
        """
        Construye un objeto Compra
        sin guardarlo en la base.
        """
        return Compra(
            pedido_item=item,
            cliente=item.pedido.cliente,
            producto=item.producto,
            cantidad=item.cantidad,
            fecha=item.pedido.fecha,
        )

    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================

    def handle(self, *args, **options):
        inicio = time.perf_counter()
        items = list(self.obtener_items_validos())
        procesados = self.obtener_items_ya_procesados()

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE COMPRAS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"PedidoItem válidos : {len(items)}")
        self.stdout.write(f"Compras existentes : {len(procesados)}")
        self.stdout.write("=" * 60)

        if len(items) == 0:
            self.stdout.write(self.style.ERROR("No existen PedidoItem válidos."))
            return

        self.stdout.write("")
        self.stdout.write("Generando compras...")

        compras = []
        compras_creadas = 0
        compras_omitidas = 0

        for item in items:
            # Ya existe una compra para este PedidoItem
            if item.id_pedido_item in procesados:
                compras_omitidas += 1
                continue

            compras.append(self.crear_compra(item))
            compras_creadas += 1

        self.stdout.write("")
        self.stdout.write(f"Compras preparadas : {compras_creadas}")
        self.stdout.write(f"Compras omitidas   : {compras_omitidas}")

        if compras_creadas == 0:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("No existen compras nuevas para insertar."))
            return

        self.stdout.write("")
        self.stdout.write("Insertando compras...")

        with transaction.atomic():
            Compra.objects.bulk_create(compras, batch_size=500)

        fin = time.perf_counter()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Compras creadas correctamente: {compras_creadas}"))
        self.stdout.write("")
        self.stdout.write("Resumen")
        self.stdout.write("-" * 60)
        self.stdout.write(f"PedidoItem procesados : {len(items)}")
        self.stdout.write(f"Compras insertadas    : {compras_creadas}")
        self.stdout.write(f"Compras omitidas      : {compras_omitidas}")
        self.stdout.write("-" * 60)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos"))