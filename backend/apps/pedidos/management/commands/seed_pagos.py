"""
Comando para generar pagos históricos de prueba.

Uso:

python manage.py seed_pagos

Características:

- Genera pagos coherentes según el estado del pedido.
- No modifica pedidos.
- No modifica clientes.
- No modifica productos.
- No genera pagos para pedidos cancelados.
- Respeta la relación OneToOne entre Pedido y Pago.
- Utiliza bulk_create para rendimiento.
"""


from django.core.management.base import BaseCommand

from django.db import transaction

from django.utils import timezone

from apps.pedidos.models import (
    Pedido,
    Pago,
)

from utils.seed.config import (
    PORCENTAJE_PAGOS_APROBADOS,
    PORCENTAJE_PAGOS_RECHAZADOS,
)

import random

import time

from datetime import timedelta



class Command(BaseCommand):

    help = "Genera pagos históricos de prueba."


    # =====================================================
    # ARGUMENTOS
    # =====================================================

    def add_arguments(
        self,
        parser
    ):

        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Regenera pagos eliminando los existentes."
        )



    # =====================================================
    # OBTENER PEDIDOS
    # =====================================================

    def obtener_pedidos_sin_pago(
        self
    ):

        """
        Obtiene pedidos que todavía
        no tienen pago asociado.

        Excluye pedidos cancelados.
        """

        return Pedido.objects.exclude(
            estado="cancelado"
        ).exclude(
            pago__isnull=False
        )



    # =====================================================
    # METODO DE PAGO
    # =====================================================

    def generar_metodo_pago(
        self
    ):

        """
        Distribución realista de métodos
        de pago utilizados.
        """

        return random.choices(

            [

                "tarjeta",

                "debito",

                "transferencia",

                "efectivo",

            ],

            weights=[

                45,

                25,

                20,

                10,

            ]

        )[0]



    # =====================================================
    # ESTADO DEL PAGO
    # =====================================================

    def determinar_estado_pago(
        self,
        pedido
    ):

        """
        Determina el estado del pago
        dependiendo del estado del pedido.
        """

        if pedido.estado == "pendiente":

            return "pendiente"



        if pedido.estado == "pagado":

            return "aprobado"



        if pedido.estado in [

            "entregado",

            "enviado",

        ]:


            resultado = random.random()


            if resultado <= PORCENTAJE_PAGOS_APROBADOS:

                return "aprobado"


            elif resultado <= (

                PORCENTAJE_PAGOS_APROBADOS
                +
                PORCENTAJE_PAGOS_RECHAZADOS

            ):

                return "rechazado"


            else:

                return "pendiente"



        return "pendiente"

    # =====================================================
    # FECHA DE PAGO
    # =====================================================

    def generar_fecha_pago(
        self,
        pedido,
        estado_pago
    ):

        """
        Genera una fecha de pago coherente.

        Reglas:

        - Pagos aprobados:
            fecha entre pedido.fecha
            y hasta 5 días después.

        - Pagos rechazados:
            intento de pago cercano
            a la fecha del pedido.

        - Pagos pendientes:
            sin fecha.
        """


        if estado_pago == "pendiente":

            return None



        dias = random.randint(
            0,
            5
        )


        return pedido.fecha + timedelta(
            days=dias
        )



    # =====================================================
    # CREAR PAGO
    # =====================================================

    def crear_pago(
        self,
        pedido
    ):

        """
        Crea un objeto Pago
        sin guardarlo en la base de datos.
        """


        estado_pago = self.determinar_estado_pago(
            pedido
        )


        return Pago(

            pedido=pedido,

            metodo_pago=self.generar_metodo_pago(),

            monto=pedido.total,

            fecha_pago=self.generar_fecha_pago(
                pedido,
                estado_pago
            ),

            estado=estado_pago

        )



    # =====================================================
    # ELIMINAR PAGOS EXISTENTES
    # =====================================================

    def eliminar_pagos_existentes(
        self
    ):

        """
        Elimina todos los pagos existentes.

        Se utiliza únicamente con --forzar.
        """

        cantidad = Pago.objects.count()


        Pago.objects.all().delete()


        return cantidad



    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================

    def handle(
        self,
        *args,
        **options
    ):


        inicio = time.perf_counter()



        forzar = options["forzar"]



        self.stdout.write("")

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            "GENERADOR DE PAGOS"
        )

        self.stdout.write(
            "=" * 60
        )



        self.stdout.write(
            f"Pedidos totales : {Pedido.objects.count()}"
        )


        self.stdout.write(
            f"Pagos existentes: {Pago.objects.count()}"
        )



        self.stdout.write(
            "=" * 60
        )



        # =================================================
        # ELIMINACIÓN OPCIONAL
        # =================================================


        if forzar:


            eliminados = self.eliminar_pagos_existentes()


            self.stdout.write("")


            self.stdout.write(

                self.style.WARNING(

                    f"Pagos eliminados: {eliminados}"

                )

            )



        # =================================================
        # OBTENER PEDIDOS
        # =================================================


        pedidos = list(

            self.obtener_pedidos_sin_pago()

        )



        self.stdout.write("")


        self.stdout.write(

            f"Pedidos candidatos: {len(pedidos)}"

        )



        if not pedidos:


            self.stdout.write("")


            self.stdout.write(

                self.style.SUCCESS(

                    "No existen pedidos pendientes de pago."

                )

            )


            return



        self.stdout.write("")


        self.stdout.write(

            "Generando pagos..."

        )



        pagos = []



        for pedido in pedidos:


            pagos.append(

                self.crear_pago(

                    pedido

                )

            )



        self.stdout.write(

            f"Pagos preparados: {len(pagos)}"

        )



        self.stdout.write("")


        self.stdout.write(

            "Insertando pagos..."

        )



        # =================================================
        # INSERCIÓN MASIVA
        # =================================================


        with transaction.atomic():


            Pago.objects.bulk_create(

                pagos,

                batch_size=500

            )

        # =================================================
        # ESTADÍSTICAS
        # =================================================

        estados = {}

        metodos = {}


        for pago in pagos:


            estados[pago.estado] = (

                estados.get(
                    pago.estado,
                    0
                )
                +
                1

            )


            metodos[pago.metodo_pago] = (

                metodos.get(
                    pago.metodo_pago,
                    0
                )
                +
                1

            )



        fin = time.perf_counter()



        # =================================================
        # RESUMEN FINAL
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            "RESUMEN PAGOS"
        )

        self.stdout.write(
            "=" * 60
        )



        self.stdout.write(
            f"Pagos creados: {len(pagos)}"
        )



        self.stdout.write("")


        self.stdout.write(
            "Estados:"
        )


        for estado, cantidad in estados.items():


            self.stdout.write(

                f"  {estado.capitalize():15}: {cantidad}"

            )



        self.stdout.write("")


        self.stdout.write(
            "Métodos de pago:"
        )


        for metodo, cantidad in metodos.items():


            self.stdout.write(

                f"  {metodo.capitalize():15}: {cantidad}"

            )



        self.stdout.write("")


        self.stdout.write(
            "-" * 60
        )


        self.stdout.write(

            self.style.SUCCESS(

                f"Tiempo total: {fin - inicio:.2f} segundos"

            )

        )