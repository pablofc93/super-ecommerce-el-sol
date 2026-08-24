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

User = get_user_model() #se trabaja con el modelo Usuarios
fake = Faker("es_AR") #define que los datos Fake van a ser de Argentina

#esta es la clase que representa al comando en sí
class Command(BaseCommand):

    help = "Genera usuarios de prueba."

    def add_arguments(self, parser):
        parser.add_argument( #parser es un objeto que se usa para definir los argumentos que puede recibir el comando desde la terminal
            "--cantidad",
            type=int,
            default=2500,
            help="Cantidad de usuarios a generar."
        )

    def obtener_usuarios_existentes(self):
        """
        Devuelve la cantidad de usuarios de tipo cliente existentes. Consulta a la base de datos
        """
        return User.objects.filter(tipo_usuario="cliente").count()

    #este método se encarga de determinar cual es el próx num utilizado para generar un username cliente.
    def obtener_siguiente_numero(self):
        """
        Devuelve el siguiente número disponible para usernames
        con formato cliente000001.
        """

        #expresión regular que busca encontrar todos los clientes que coincidan con el patrón 
        #cliente000001, cliente000002, etc. y extrae el número de 6 dígitos.
        patron = re.compile(r"^cliente(\d{6})$") 

        mayor = 0 #guarda el número más grande encontrado hasta ahora

        #Django consulta el modelo User y obtiene todos los usernames existentes en la base de datos.
        usernames = User.objects.values_list(
            "username",
            flat=True
        )

        #se comienzan a recorrer los usuarios 
        for username in usernames:
            coincidencia = patron.match(username) #se comprueba si el cliente analizado coincide con el patrón. ej: cliente000025
            if coincidencia:
                numero = int(coincidencia.group(1)) #aqui se captura el numero que acompaña al nombre del cliente. ej: 00025, es texto, con int se lo pasa a num
                if numero > mayor: #se compara si el numero encontrado es mayor que el que ya se tenia
                    mayor = numero
        return mayor + 1


    def generar_usuario(self, numero, password_hash):
        """
        Genera un objeto Usuario sin guardarlo en la base de datos.
        """

        ahora = timezone.now()

        #genera una fecha de registro aleatoria entre hace 2 años y ahora, con la misma zona horaria que la fecha actual.
        fecha_registro = fake.date_time_between(
            start_date="-2y",
            end_date="now",
            tzinfo=ahora.tzinfo #indica la zona horaria que debe utilizar la fecha generada
        )

        ultimo_login = None

        # Aproximadamente el 80% inició sesión alguna vez
        if random.random() < 0.80:
            ultimo_login = fake.date_time_between(
                start_date=fecha_registro,
                end_date="now",
                tzinfo=ahora.tzinfo
            )

        # construcción del username del cliente, con el formato cliente000001, cliente000002, etc. 
        # El número se rellena con ceros a la izquierda para que siempre tenga 6 dígitos.
        username = f"cliente{numero:06d}"

        #devuelvo un objeto Usuario con los datos generados, pero sin guardarlo en la base de datos todavía.
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

        #comprobar si el admin ya existe
        if User.objects.filter(username=username).exists():
            return False, username

        ahora = timezone.now() #obtiene la fecha y hora actual para la propiedad de date_joined del usuario admin

        #aqui crea el objeto y lo guarda en la base de datos .create() almacena inmediatamente el objeto admin en la bd
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
    
    #es el método principal que se ejecuta cuando se llama al comando desde la terminal. Es el encargado de coordinar los otros métodos
    #*args permite recibir argumentos posicionales pero actualmente no se utiliza
    #**options permite recibir argumentos con nombre, como --cantidad
    def handle(self, *args, **options):
        inicio = time.perf_counter() #obtiene el tiempo actual en segundos para medir cuanto tarda en ejecutarse el comando
        cantidad = options["cantidad"] #obtiene la cantidad de usuarios a generar desde los argumentos del comando
        existentes = self.obtener_usuarios_existentes() #obtiene la cantidad de usuarios cliente que ya existen en la base de datos
        faltantes = max(cantidad - existentes, 0) #calcula cuántos usuarios faltan por crear para llegar a la cantidad solicitada. Si ya existen suficientes usuarios, faltantes será 0.
        siguiente_numero = self.obtener_siguiente_numero() #obtiene el siguiente número disponible para generar un username cliente, por ejemplo si ya existen cliente000001 y cliente000002, siguiente_numero será 3.
        print("DEBUG -> siguiente_numero =", siguiente_numero)
        password_hash = make_password("123456") #genera la misma contraseña para todos los usuarios clientes y la hashea

        #esto muestra información por consola
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
        #crea una tramsacción atómica en la base de datos
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

        usuarios = [] #lista que almacenará temporalmente los objetos User(Usuarios)

        #aqui se genera cada usuario cliente y se agrega a la lista usuarios. 
        # Se utiliza un bucle for que va desde el siguiente_numero hasta el siguiente_numero + faltantes, 
        # generando así los usernames de manera secuencial.
        for i in range(
            siguiente_numero,
            siguiente_numero + faltantes
        ):
            usuarios.append(

                self.generar_usuario(i, password_hash)
            )

        with transaction.atomic():

            #carga todos los usuarios juntos en lugar de guardarlos uno por uno separados
            User.objects.bulk_create(
                usuarios,
                batch_size=500 #esto significa que se insertarán 500 usuarios a la vez en la base de datos, lo que mejora el rendimiento
            )

            self.stdout.write("")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Se crearon {faltantes} usuarios correctamente." #muestra la cantidad de usuarios creados
                )
            )

        fin = time.perf_counter() #calcula el momento de finalización del proceso

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Tiempo total: {fin - inicio:.2f} segundos" #muestra el tiempo total de ejecución del proceso
            )
        )