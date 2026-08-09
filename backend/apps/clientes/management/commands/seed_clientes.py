"""
Comando para generar clientes de prueba.

Uso:

python manage.py seed_clientes

python manage.py seed_clientes --cantidad 2500
"""


from django.core.management.base import BaseCommand

from django.db import transaction

from django.contrib.auth import get_user_model

from faker import Faker



import random

import time


from apps.clientes.models import Cliente

from utils.seed.faker_config import fake

from utils.seed.helpers import (
    generar_ubicacion,
    generar_codigo_postal,
    generar_telefono,
)

User = get_user_model()


class Command(BaseCommand):

    help = "Genera clientes asociados a usuarios tipo cliente."


    def add_arguments(self, parser):

        parser.add_argument(
            "--cantidad",
            type=int,
            default=2500,
            help="Cantidad total de clientes que deben existir."
        )



    def obtener_clientes_existentes(self):

        return Cliente.objects.count()



    def obtener_usuarios_sin_cliente(self):

        """
        Obtiene usuarios tipo cliente
        que todavía no poseen perfil Cliente.
        """

        usuarios_con_cliente = Cliente.objects.values_list(
            "id_cliente_id",
            flat=True
        )


        return User.objects.filter(
            tipo_usuario="cliente"
        ).exclude(
            id__in=usuarios_con_cliente
        )



    def generar_cliente(self, usuario):

        provincia, ciudad = generar_ubicacion()

        return Cliente(

            id_cliente=usuario,
            telefono=generar_telefono(),
            direccion=fake.street_address(),
            ciudad=ciudad,
            provincia=provincia,
            codigo_postal=generar_codigo_postal(),

        )



    def handle(self, *args, **options):

        inicio = time.perf_counter()


        cantidad = options["cantidad"]


        existentes = self.obtener_clientes_existentes()


        faltantes = max(
            cantidad - existentes,
            0
        )


        self.stdout.write("")

        self.stdout.write("=" * 60)

        self.stdout.write(
            "GENERADOR DE CLIENTES"
        )

        self.stdout.write("=" * 60)

        self.stdout.write(
            f"Cantidad solicitada: {cantidad}"
        )

        self.stdout.write(
            f"Clientes existentes: {existentes}"
        )

        self.stdout.write(
            f"Clientes a crear: {faltantes}"
        )

        self.stdout.write("=" * 60)



        if faltantes == 0:

            self.stdout.write("")

            self.stdout.write(
                self.style.SUCCESS(
                    "Ya existen suficientes clientes. No es necesario crear nuevos."
                )
            )

            return



        usuarios_disponibles = list(
            self.obtener_usuarios_sin_cliente()
        )



        if len(usuarios_disponibles) < faltantes:

            self.stdout.write("")

            self.stdout.write(

                self.style.ERROR(

                    "No existen suficientes usuarios tipo cliente disponibles."

                )

            )

            self.stdout.write(

                f"Usuarios disponibles: {len(usuarios_disponibles)}"

            )

            return



        self.stdout.write("")

        self.stdout.write(
            "Generando clientes..."
        )



        clientes = []


        for usuario in usuarios_disponibles[:faltantes]:

            clientes.append(

                self.generar_cliente(usuario)

            )



        with transaction.atomic():


            Cliente.objects.bulk_create(

                clientes,

                batch_size=500

            )


        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Se crearon {faltantes} clientes correctamente."

            )

        )


        fin = time.perf_counter()


        self.stdout.write("")

        self.stdout.write(

            self.style.SUCCESS(

                f"Tiempo total: {fin - inicio:.2f} segundos"

            )

        )