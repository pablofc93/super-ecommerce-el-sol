"""
Comando para generar usuarios de prueba.

Uso:

python manage.py seed_usuarios

python manage.py seed_usuarios --cantidad 2500
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from faker import Faker
from datetime import timedelta
import random
import time
import re
from django.db.models import Max

User = get_user_model()
fake = Faker("es_AR")


class Command(BaseCommand):

    help = "Genera usuarios de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cantidad",
            type=int,
            default=2500,
            help="Cantidad de usuarios a generar."
        )

    def obtener_usuarios_existentes(self):
        """
        Devuelve la cantidad de usuarios de tipo cliente existentes.
        """
        return User.objects.filter(tipo_usuario="cliente").count()

    def obtener_siguiente_numero(self):
        """
        Devuelve el siguiente número disponible para usernames
        con formato cliente000001.
        """

        patron = re.compile(r"^cliente(\d{6})$")

        mayor = 0

        usernames = User.objects.values_list(
            "username",
            flat=True
        )

        for username in usernames:

            coincidencia = patron.match(username)

            if coincidencia:

                numero = int(coincidencia.group(1))

                if numero > mayor:
                    mayor = numero

        return mayor + 1

    def generar_usuario(self, numero, password_hash):
        """
        Genera un objeto Usuario sin guardarlo en la base de datos.
        """

        ahora = timezone.now()

        fecha_registro = fake.date_time_between(
            start_date="-2y",
            end_date="now",
            tzinfo=ahora.tzinfo
        )

        ultimo_login = None

        # Aproximadamente el 80% inició sesión alguna vez
        if random.random() < 0.80:
            ultimo_login = fake.date_time_between(
                start_date=fecha_registro,
                end_date="now",
                tzinfo=ahora.tzinfo
            )

        username = f"cliente{numero:06d}"

        return User(
            username=username,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=f"{username}@test.com",
            tipo_usuario="cliente",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            password=password_hash,
            date_joined=fecha_registro,
            last_login=ultimo_login,
        )

    def obtener_o_crear_admin(self, password_hash):
        """
        Crea un usuario admin de prueba si todavía no existe.
        Devuelve una tupla (creado: bool, username: str).
        """

        username = "admin_test"

        if User.objects.filter(username=username).exists():
            return False, username

        ahora = timezone.now()

        User.objects.create(
            username=username,
            first_name="Admin",
            last_name="Test",
            email=f"{username}@test.com",
            tipo_usuario="admin",
            is_active=True,
            is_staff=True,
            is_superuser=True,
            password=password_hash,
            date_joined=ahora,
            last_login=None,
        )

        return True, username

    def handle(self, *args, **options):

        inicio = time.perf_counter()

        cantidad = options["cantidad"]

        existentes = self.obtener_usuarios_existentes()

        faltantes = max(cantidad - existentes, 0)

        siguiente_numero = self.obtener_siguiente_numero()

        print("DEBUG -> siguiente_numero =", siguiente_numero)

        password_hash = make_password("123456")

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("GENERADOR DE USUARIOS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Cantidad solicitada: {cantidad}")
        self.stdout.write(f"Usuarios existentes: {existentes}")
        self.stdout.write(f"Usuarios a crear: {faltantes}")
        self.stdout.write(f"Primer username: cliente{siguiente_numero:06d}")
        self.stdout.write("=" * 60)

        # --- Usuario admin de prueba ---
        with transaction.atomic():
            admin_creado, admin_username = self.obtener_o_crear_admin(password_hash)

        self.stdout.write("")
        if admin_creado:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario admin de prueba creado: {admin_username} (password: 123456)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"El usuario admin de prueba '{admin_username}' ya existía. No se creó de nuevo."
                )
            )

        if faltantes == 0:

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Ya existen suficientes usuarios cliente. No es necesario crear nuevos."
                )
            )

            return

        self.stdout.write("")
        self.stdout.write("Generando usuarios cliente...")

        usuarios = []

        for i in range(
            siguiente_numero,
            siguiente_numero + faltantes
        ):
            usuarios.append(

                self.generar_usuario(i, password_hash)
            )

        with transaction.atomic():

            User.objects.bulk_create(
                usuarios,
                batch_size=500
            )

            self.stdout.write("")

            self.stdout.write(

                self.style.SUCCESS(

                    f"Se crearon {faltantes} usuarios correctamente."

                )

            )

        fin = time.perf_counter()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Tiempo total: {fin - inicio:.2f} segundos"
            )
        )