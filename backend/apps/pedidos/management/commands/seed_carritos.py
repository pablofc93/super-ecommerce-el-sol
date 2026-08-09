"""
Comando para generar carritos de prueba.

Uso:

python manage.py seed_carritos

python manage.py seed_carritos --cantidad 2500
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.clientes.models import Cliente
from apps.pedidos.models import Carrito

from utils.seed.config import PORCENTAJE_CARRITOS_ACTIVOS

import random
import time


class Command(BaseCommand):

    help = "Genera carritos de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cantidad",
            type=int,
            default=2500,
            help="Cantidad de carritos a generar."
        )

    def obtener_carritos_existentes(self):
        """
        Devuelve la cantidad de carritos existentes.
        """
        return Carrito.objects.count()

    def obtener_clientes_sin_carrito(self):
        """
        Devuelve los clientes que todavía no poseen carrito.
        """

        return Cliente.objects.filter(
            carrito__isnull=True
        ).order_by("id_cliente")

    def generar_carrito(self, cliente):
        """
        Genera un objeto Carrito sin guardarlo en la base de datos.
        """

        return Carrito(
            cliente=cliente,
            activo=random.random() < PORCENTAJE_CARRITOS_ACTIVOS
        )

    def handle(self, *args, **options):

        inicio = time.perf_counter()

        cantidad = options["cantidad"]

        existentes = self.obtener_carritos_existentes()

        faltantes = max(cantidad - existentes, 0)

        clientes = list(
            self.obtener_clientes_sin_carrito()[:faltantes]
        )

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE CARRITOS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Cantidad solicitada : {cantidad}")
        self.stdout.write(f"Carritos existentes : {existentes}")
        self.stdout.write(f"Carritos a crear    : {len(clientes)}")
        self.stdout.write("=" * 60)

        if len(clientes) == 0:

            self.stdout.write("")

            self.stdout.write(

                self.style.SUCCESS(

                    "Todos los clientes ya poseen un carrito."

                )

            )

            return

        self.stdout.write("")
        self.stdout.write("Generando carritos...")

        carritos = []

        activos = 0
        inactivos = 0

        for cliente in clientes:

            carrito = self.generar_carrito(cliente)

            if carrito.activo:
                activos += 1
            else:
                inactivos += 1

            carritos.append(carrito)

        with transaction.atomic():

            Carrito.objects.bulk_create(
                carritos,
                batch_size=500
            )

        fin = time.perf_counter()

        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Se crearon {len(carritos)} carritos correctamente."

            )

        )

        self.stdout.write("")
        self.stdout.write("Resumen")
        self.stdout.write("-" * 60)
        self.stdout.write(f"Carritos activos   : {activos}")
        self.stdout.write(f"Carritos inactivos : {inactivos}")
        self.stdout.write("-" * 60)

        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Tiempo total: {fin - inicio:.2f} segundos"

            )

        )