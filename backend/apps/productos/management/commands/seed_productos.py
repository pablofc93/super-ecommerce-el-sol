"""
Comando para cargar productos desde utils/seed/productos.txt.

Uso:
    python manage.py seed_productos

Características:
- Lee todos los productos desde utils/seed/productos.txt.
- Cada fila del TXT representa un producto independiente.
- NO utiliza el ID original del TXT como ID de la base de datos.
- Los IDs de Django son generados automáticamente.
- Permite productos repetidos o con datos idénticos.
- NO elimina duplicados.
- NO compara productos por sus datos.
- Inserta todos los registros encontrados en productos.txt.
- Solamente permite realizar la carga UNA VEZ.
- Si productos_producto ya contiene registros, el seed se detiene.
- Convierte correctamente precios con formato argentino.
- Convierte correctamente stocks con separador de miles.
- Verifica que todas las categorías utilizadas existan.
- Utiliza bulk_create() para realizar la carga rápidamente.
- Actualiza sqlite_sequence cuando corresponde.

IMPORTANTE:
Este seed es de ejecución única.

Primera ejecución:
    productos_producto = 0 registros
    productos.txt = 1016 registros

Resultado:
    productos_producto = 1016 registros

Segunda ejecución:
    productos_producto = 1016 registros

Resultado:
    No se realiza ninguna inserción.

El contenido de productos.txt puede contener productos repetidos.
Cada fila se considera un producto independiente.
"""

import re
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from apps.productos.models import Producto


class Command(BaseCommand):

    help = "Carga todos los productos desde productos.txt una única vez."

    # =====================================================
    # RUTA DEL ARCHIVO
    # =====================================================
    def obtener_ruta_archivo(self):
        """Devuelve la ruta absoluta del archivo productos.txt."""
        return Path(__file__).resolve().parents[4] / "utils" / "seed" / "productos.txt"

    # =====================================================
    # CONVERTIR PRECIO
    # =====================================================
    def convertir_precio(self, valor):
        """
        Convierte precios escritos con formato argentino.

        Ejemplos:
        4.143,39 -> 4143.39
        359,99   -> 359.99
        1.060    -> 1060.00
        7.900    -> 7900.00
        999      -> 999.00
        """
        valor = str(valor).strip()

        if not valor:
            raise ValueError("El precio está vacío.")

        valor = valor.replace("$", "").replace(" ", "")

        if "," in valor:
            # Ejemplo: 4.143,39 -> 4143.39
            valor = valor.replace(".", "").replace(",", ".")
        else:
            partes = valor.split(".")
            # Ejemplos: 4.143 -> 4143 | 7.900 -> 7900
            if len(partes) == 2 and len(partes[1]) == 3:
                valor = "".join(partes)

        try:
            return Decimal(valor).quantize(Decimal("0.01"))
        except InvalidOperation as error:
            raise ValueError(f"Precio inválido: {valor}") from error

    # =====================================================
    # CONVERTIR STOCK
    # =====================================================
    def convertir_stock(self, valor):
        """
        Convierte stocks escritos con formato argentino.

        Ejemplos:
        43.432 -> 43432
        1.546  -> 1546
        200    -> 200
        """
        valor = str(valor).strip().replace(".", "")

        if not valor:
            raise ValueError("El stock está vacío.")

        try:
            stock = int(valor)
        except ValueError as error:
            raise ValueError(f"Stock inválido: {valor}") from error

        if stock < 0:
            raise ValueError(f"El stock no puede ser negativo: {stock}")

        return stock

    # =====================================================
    # OBTENER FILAS
    # =====================================================
    def obtener_filas(self, ruta):
        """
        Lee productos.txt. Cada fila cuyo primer campo sea numérico
        representa un producto independiente. NO se eliminan duplicados.

        Se aceptan dos formatos:

        FORMATO 1:
        |id|nombre|descripcion|precio|stock|imagen|categoria_id|

        FORMATO 2:
        |id|nombre|descripcion|precio|creado_en|actualizado_en|categoria_id|imagen|stock|

        En el formato 2 se ignoran creado_en y actualizado_en.
        """
        productos = []

        with ruta.open("r", encoding="utf-8-sig") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()

                # Ignorar líneas vacías
                if not linea:
                    continue

                # Ignorar líneas que no comienzan con "|"
                if not linea.startswith("|"):
                    continue

                # Ignorar encabezados y separadores Markdown.
                # Solamente se procesan líneas cuyo primer campo sea un número.
                if not re.match(r"^\|\s*\d+\s*\|", linea):
                    continue

                # Separar columnas
                partes = [parte.strip() for parte in linea.split("|")]

                # Eliminar columna vacía inicial
                if partes and partes[0] == "":
                    partes.pop(0)

                # Eliminar columna vacía final
                if partes and partes[-1] == "":
                    partes.pop()

                # FORMATO DE 7 COLUMNAS
                if len(partes) == 7:
                    (
                        id_original,
                        nombre,
                        descripcion,
                        precio,
                        stock,
                        imagen,
                        categoria_id,
                    ) = partes

                # FORMATO DE 9 COLUMNAS
                elif len(partes) == 9:
                    (
                        id_original,
                        nombre,
                        descripcion,
                        precio,
                        creado_en,
                        actualizado_en,
                        categoria_id,
                        imagen,
                        stock,
                    ) = partes

                else:
                    raise CommandError(
                        f"Línea {numero_linea}: formato inválido. "
                        f"Se encontraron {len(partes)} columnas. Se esperaban 7 o 9."
                    )

                # Convertir datos. Se valida que exista un ID numérico
                # pero NO se utiliza para el ID de Django.
                try:
                    id_original = int(id_original)
                    precio_convertido = self.convertir_precio(precio)
                    stock_convertido = self.convertir_stock(stock)
                    categoria_id = int(categoria_id)
                except (ValueError, TypeError) as error:
                    raise CommandError(f"Error en línea {numero_linea}: {error}") from error

                # Validar nombre
                if not nombre:
                    raise CommandError(
                        f"Línea {numero_linea}: el nombre del producto está vacío."
                    )

                # Agregar producto. No se utiliza ningún conjunto (set)
                # para detectar duplicados; cada fila genera un producto.
                productos.append({
                    "numero_linea": numero_linea,
                    "id_original": id_original,
                    "nombre": nombre,
                    "descripcion": descripcion if descripcion else None,
                    "precio": precio_convertido,
                    "stock": stock_convertido,
                    "imagen": imagen if imagen else None,
                    "categoria_id": categoria_id,
                })

        return productos

    # =====================================================
    # VERIFICAR CATEGORÍAS
    # =====================================================
    def verificar_categorias(self, productos):
        """
        Verifica que todas las categorías utilizadas por productos.txt
        existan. No crea ni modifica categorías.
        """
        categoria_ids = {
            producto["categoria_id"]
            for producto in productos
            if producto["categoria_id"] is not None
        }

        if not categoria_ids:
            return

        placeholders = ",".join(["%s"] * len(categoria_ids))

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id FROM productos_categoria WHERE id IN ({placeholders})",
                list(categoria_ids),
            )
            categorias_existentes = {fila[0] for fila in cursor.fetchall()}

        categorias_faltantes = categoria_ids - categorias_existentes

        if categorias_faltantes:
            raise CommandError(
                "No existen las siguientes categorías en productos_categoria: "
                f"{sorted(categorias_faltantes)}"
            )

    # =====================================================
    # CREAR OBJETOS PRODUCTO
    # =====================================================
    def crear_objetos_productos(self, productos):
        """
        Convierte todas las filas del TXT en objetos Producto.
        Cada fila representa un producto independiente. NO se eliminan
        duplicados, NO se compara con otros productos, NO se establece
        el ID.
        """
        ahora = timezone.now()

        return [
            Producto(
                nombre=producto["nombre"],
                descripcion=producto["descripcion"],
                precio=producto["precio"],
                stock=producto["stock"],
                imagen=producto["imagen"],
                categoria_id=producto["categoria_id"],
                creado_en=ahora,
                actualizado_en=ahora,
            )
            for producto in productos
        ]

    # =====================================================
    # ACTUALIZAR SECUENCIA SQLITE
    # =====================================================
    def actualizar_secuencia(self):
        """Actualiza sqlite_sequence después de insertar todos los productos."""
        if connection.vendor != "sqlite":
            return

        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM productos_producto")
            resultado = cursor.fetchone()
            max_id = resultado[0] if resultado and resultado[0] is not None else None

            if max_id is not None:
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = %s "
                    "WHERE name = 'productos_producto'",
                    [max_id],
                )

                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO sqlite_sequence (name, seq) "
                        "VALUES ('productos_producto', %s)",
                        [max_id],
                    )

    # =====================================================
    # VALIDAR CANTIDAD FINAL
    # =====================================================
    def validar_cantidad_final(self, cantidad_txt):
        """
        Comprueba que la cantidad de registros de la BD coincida
        exactamente con la cantidad de registros encontrados en
        productos.txt.
        """
        cantidad_bd = Producto.objects.count()

        if cantidad_bd != cantidad_txt:
            raise CommandError(
                "\nERROR DE VALIDACIÓN.\n\n"
                f"Productos encontrados en TXT : {cantidad_txt}\n"
                f"Productos encontrados en BD  : {cantidad_bd}\n\n"
                "La cantidad de registros no coincide."
            )

        return cantidad_bd

    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================
    def handle(self, *args, **options):
        inicio = time.perf_counter()
        ruta = self.obtener_ruta_archivo()

        # ENCABEZADO
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("CARGADOR DE PRODUCTOS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Archivo: {ruta}")
        self.stdout.write("=" * 60)

        # VERIFICAR ARCHIVO
        if not ruta.exists():
            raise CommandError(f"No se encontró el archivo:\n{ruta}")

        # VERIFICAR SI YA FUE EJECUTADO
        cantidad_bd = Producto.objects.count()

        if cantidad_bd > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("EL SEED DE PRODUCTOS YA FUE EJECUTADO.")
            )
            self.stdout.write("")
            self.stdout.write(f"Productos actualmente en BD: {cantidad_bd}")
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("No se realizará ninguna inserción.")
            )
            self.stdout.write(
                self.style.WARNING(
                    "El seed de productos solamente puede ejecutarse una vez."
                )
            )
            return

        # LEER PRODUCTOS
        self.stdout.write("")
        self.stdout.write("Leyendo productos.txt...")
        productos_archivo = self.obtener_filas(ruta)
        cantidad_txt = len(productos_archivo)
        self.stdout.write(f"Productos encontrados en archivo: {cantidad_txt}")

        # VERIFICAR QUE HAYA PRODUCTOS
        if not productos_archivo:
            raise CommandError("productos.txt no contiene ningún producto válido.")

        # VERIFICAR CATEGORÍAS
        self.stdout.write("")
        self.stdout.write("Verificando categorías...")
        self.verificar_categorias(productos_archivo)
        self.stdout.write(self.style.SUCCESS("Todas las categorías existen."))

        # CREAR OBJETOS
        self.stdout.write("")
        self.stdout.write("Preparando productos...")
        objetos_productos = self.crear_objetos_productos(productos_archivo)
        self.stdout.write(f"Productos preparados: {len(objetos_productos)}")

        # INSERTAR
        self.stdout.write("")
        self.stdout.write("Insertando productos...")

        with transaction.atomic():
            Producto.objects.bulk_create(objetos_productos, batch_size=500)
            self.actualizar_secuencia()

        # VALIDACIÓN FINAL
        total_bd = self.validar_cantidad_final(cantidad_txt)

        # OBTENER IDS
        primer_id = Producto.objects.order_by("id").values_list("id", flat=True).first()
        ultimo_id = Producto.objects.order_by("-id").values_list("id", flat=True).first()

        # TIEMPO
        fin = time.perf_counter()

        # RESULTADO
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("CARGA COMPLETADA CORRECTAMENTE"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Registros encontrados en TXT : {cantidad_txt}")
        self.stdout.write(f"Registros insertados en BD   : {total_bd}")
        self.stdout.write(f"Primer ID generado           : {primer_id}")
        self.stdout.write(f"Último ID generado           : {ultimo_id}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "VALIDACIÓN CORRECTA: todos los registros de productos.txt "
                "fueron insertados."
            )
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos"))