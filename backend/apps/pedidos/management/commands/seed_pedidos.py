"""
Comando para generar pedidos históricos de prueba.

Uso:

python manage.py seed_pedidos

python manage.py seed_pedidos --cantidad 20000


Características:

- Genera pedidos históricos.
- No modifica stock.
- No modifica carritos.
- No genera PedidoItem.
- No genera Pago.
- total queda NULL hasta seed_pedidoitems.py.
- Permite clientes sin pedidos.
- Distribución realista de clientes compradores.
"""


from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.pedidos.models import Pedido

from utils.seed.config import (
    PORCENTAJE_CLIENTES_CON_PEDIDOS,
)

import random
import time

from datetime import timedelta



class Command(BaseCommand):

    help = "Genera pedidos históricos de prueba."


    def add_arguments(self, parser):

        parser.add_argument(
            "--cantidad",
            type=int,
            default=20000,
            help="Cantidad total de pedidos a generar."
        )



    # =====================================================
    # FECHAS HISTÓRICAS
    # =====================================================

    def generar_fecha_historica(self):

        """
        Genera fechas dentro de los últimos 3 años.

        Mayor concentración en fechas recientes.
        Nunca genera fechas futuras.
        """

        ahora = timezone.now()


        dias_atras = int(
            random.triangular(
                0,
                365 * 3,
                250
            )
        )


        return ahora - timedelta(
            days=dias_atras
        )



    # =====================================================
    # ESTADOS
    # =====================================================

    def determinar_estado(
        self,
        fecha
    ):

        antiguedad = (
            timezone.now() - fecha
        ).days


        # Pedidos recientes
        if antiguedad <= 7:

            return random.choices(

                [
                    "pendiente",
                    "pagado",
                    "enviado"
                ],

                weights=[
                    40,
                    40,
                    20
                ]

            )[0]



        # Pedidos intermedios
        elif antiguedad <= 30:

            return random.choices(

                [
                    "pagado",
                    "enviado",
                    "entregado"
                ],

                weights=[
                    20,
                    40,
                    40
                ]

            )[0]



        # Pedidos antiguos

        return random.choices(

            [
                "entregado",
                "cancelado",
                "enviado"
            ],

            weights=[
                80,
                10,
                10
            ]

        )[0]



    # =====================================================
    # SELECCIONAR CLIENTES
    # =====================================================

    def obtener_clientes_compradores(self):

        """
        Selecciona aproximadamente el porcentaje
        definido en config.py.
        """

        clientes = list(
            Cliente.objects.all()
        )


        cantidad = int(

            len(clientes)
            *
            PORCENTAJE_CLIENTES_CON_PEDIDOS

        )


        return random.sample(

            clientes,

            cantidad

        )



    # =====================================================
    # PESOS DE CLIENTES
    # =====================================================

    def generar_pesos_clientes(
        self,
        clientes
    ):

        """
        Algunos clientes compran mucho más
        que otros.

        1 = ocasional
        3 = normal
        8 = frecuente
        """

        pesos = []


        for cliente in clientes:

            probabilidad = random.random()


            if probabilidad < 0.60:

                peso = 1


            elif probabilidad < 0.90:

                peso = 3


            else:

                peso = 8


            pesos.append(
                peso
            )


        return pesos



    # =====================================================
    # CREAR PEDIDO
    # =====================================================

    def crear_pedido(
        self,
        cliente
    ):


        fecha = self.generar_fecha_historica()


        return Pedido(

            cliente=cliente,

            fecha=fecha,

            estado=self.determinar_estado(
                fecha
            ),

            total=None

        )



    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================

    def handle(
        self,
        *args,
        **options
    ):

        inicio = time.perf_counter()


        cantidad_objetivo = options["cantidad"]



        clientes = self.obtener_clientes_compradores()



        self.stdout.write("")

        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE PEDIDOS")
        self.stdout.write("=" * 60)


        self.stdout.write(

            f"Pedidos solicitados : {cantidad_objetivo}"

        )


        self.stdout.write(

            f"Clientes totales     : {Cliente.objects.count()}"

        )


        self.stdout.write(

            f"Clientes compradores : {len(clientes)}"

        )


        self.stdout.write("=" * 60)



        if not clientes:

            self.stdout.write(

                self.style.ERROR(

                    "No existen clientes disponibles."

                )

            )

            return



        pesos = self.generar_pesos_clientes(
            clientes
        )



        pedidos = []



        self.stdout.write("")

        self.stdout.write(
            "Generando pedidos..."
        )



        while len(pedidos) < cantidad_objetivo:


            cliente = random.choices(

                clientes,

                weights=pesos,

                k=1

            )[0]



            pedidos.append(

                self.crear_pedido(

                    cliente

                )

            )



        self.stdout.write(

            f"Pedidos preparados: {len(pedidos)}"

        )



        self.stdout.write("")

        self.stdout.write(
            "Insertando pedidos..."
        )



        with transaction.atomic():


            Pedido.objects.bulk_create(

                pedidos,

                batch_size=500

            )



        fin = time.perf_counter()



        # Estadísticas

        estados = {}


        for pedido in pedidos:

            estados[pedido.estado] = (
                estados.get(
                    pedido.estado,
                    0
                )
                +
                1
            )



        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Pedidos creados correctamente: {len(pedidos)}"

            )

        )


        self.stdout.write("")

        self.stdout.write("Resumen")

        self.stdout.write("-" * 60)



        for estado, cantidad in estados.items():

            self.stdout.write(

                f"{estado.capitalize():15}: {cantidad}"

            )


        self.stdout.write("-" * 60)



        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Tiempo total: {fin - inicio:.2f} segundos"

            )

        )