from django.core.management.base import BaseCommand

from django.db import transaction

from apps.pedidos.models import Carrito, CarritoItem

from apps.productos.models import Producto

from utils.seed.config import (
    PORCENTAJE_CARRITOS_CON_ITEMS,
    PRODUCTOS_MINIMOS_POR_CARRITO,
    PRODUCTOS_MAXIMOS_POR_CARRITO,
    CANTIDAD_MINIMA_PRODUCTO,
    CANTIDAD_MAXIMA_PRODUCTO,
)

import random

import time


class Command(BaseCommand):

    help = "Genera productos dentro de los carritos."


    def add_arguments(self, parser):

        parser.add_argument(
            "--cantidad",
            type=int,
            default=None,
            help="Cantidad máxima de carritos a procesar."
        )


    def obtener_carritos_disponibles(self):
        """
        Obtiene carritos que todavía no poseen productos.
        """

        return Carrito.objects.filter(
            items__isnull=True
        )


    def generar_item(
        self,
        carrito,
        producto
    ):
        """
        Genera un CarritoItem sin guardarlo.
        """

        return CarritoItem(

            carrito=carrito,

            producto=producto,

            cantidad=random.randint(
                CANTIDAD_MINIMA_PRODUCTO,
                CANTIDAD_MAXIMA_PRODUCTO
            ),

            precio_unitario=producto.precio

        )


    def handle(self, *args, **options):

        inicio = time.perf_counter()


        cantidad = options["cantidad"]


        carritos = list(
            self.obtener_carritos_disponibles()
        )


        if cantidad:

            carritos = carritos[:cantidad]


        productos = list(
            Producto.objects.all()
        )


        self.stdout.write("")

        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE ITEMS DE CARRITO")
        self.stdout.write("=" * 60)

        self.stdout.write(
            f"Carritos disponibles : {len(carritos)}"
        )

        self.stdout.write(
            f"Productos disponibles: {len(productos)}"
        )

        self.stdout.write("=" * 60)



        if len(carritos) == 0:

            self.stdout.write(

                self.style.SUCCESS(

                    "No existen carritos pendientes de carga."

                )

            )

            return



        if len(productos) == 0:

            self.stdout.write(

                self.style.ERROR(

                    "No existen productos cargados."

                )

            )

            return



        carritos_con_items = [

            carrito

            for carrito in carritos

            if random.random()
            <
            PORCENTAJE_CARRITOS_CON_ITEMS

        ]



        items = []


        for carrito in carritos_con_items:


            cantidad_productos = random.randint(

                PRODUCTOS_MINIMOS_POR_CARRITO,

                PRODUCTOS_MAXIMOS_POR_CARRITO

            )


            productos_elegidos = random.sample(

                productos,

                min(
                    cantidad_productos,
                    len(productos)
                )

            )


            for producto in productos_elegidos:


                items.append(

                    self.generar_item(

                        carrito,

                        producto

                    )

                )



        if len(items) == 0:

            self.stdout.write("")

            self.stdout.write(

                self.style.WARNING(

                    "No se generaron items para insertar."

                )

            )

            return



        self.stdout.write("")

        self.stdout.write(
            "Insertando items..."
        )



        with transaction.atomic():

            CarritoItem.objects.bulk_create(

                items,

                batch_size=500

            )



        fin = time.perf_counter()



        self.stdout.write("")


        self.stdout.write(

            self.style.SUCCESS(

                f"Items creados correctamente: {len(items)}"

            )

        )


        self.stdout.write("")

        self.stdout.write("Resumen")

        self.stdout.write("-" * 60)


        self.stdout.write(

            f"Carritos con items: {len(carritos_con_items)}"

        )


        self.stdout.write(

            f"Total items       : {len(items)}"

        )


        self.stdout.write("-" * 60)



        self.stdout.write("")


        self.stdout.write(

            self.style.SUCCESS(

                f"Tiempo total: {fin - inicio:.2f} segundos"

            )

        )