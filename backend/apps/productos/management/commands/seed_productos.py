"""
Comando para cargar productos desde utils/seed/productos.txt.

Uso:
    python manage.py seed_productos

Características:
- Lee todos los productos desde utils/seed/productos.txt.
- Cada fila del TXT representa un producto independiente.
- NO utiliza el ID original del TXT como ID de la base de datos.
- Los IDs de Django son generados automáticamente.
- Si la tabla está vacía, inserta todos los productos del TXT.
- Si ya existen productos, detecta cuántos registros del TXT ya fueron
  cargados y solamente inserta los nuevos.
- Permite que existan productos con datos similares o repetidos dentro del TXT.
- Conserva nombre, descripción, precio, stock, imagen y categoría.
- Convierte correctamente precios con formato argentino.
- Convierte correctamente stocks con separador de miles.
- Utiliza bulk_create() para realizar la carga rápidamente.
- Actualiza sqlite_sequence cuando corresponde.

IMPORTANTE:
El seed considera que los productos se agregan al final de productos.txt.

Por ejemplo:
    Primera ejecución:
        TXT = 800 productos
        BD  = 0 productos

    Segunda ejecución:
        TXT = 1016 productos
        BD  = 800 productos

    Resultado:
        Se insertan solamente los 216 nuevos productos.

Si se modifica un producto que ya estaba cargado en medio del TXT, el seed
detectará la diferencia y detendrá la ejecución para evitar duplicaciones
o inconsistencias.
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

    help = "Carga productos desde utils/seed/productos.txt."

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
            # Ejemplo: 4.143 -> 4143 | 7.900 -> 7900
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
        Lee productos.txt y devuelve TODOS los productos válidos.

        El archivo puede tener este formato:
        |id|nombre|descripcion|precio|stock|imagen|categoria_id|

        También acepta un TXT exportado desde una tabla que contenga
        las columnas:
        |id|nombre|descripcion|precio|creado_en|actualizado_en|categoria_id|imagen|stock|

        En este segundo caso se ignoran creado_en y actualizado_en.
        """
        productos = []

        with ruta.open("r", encoding="utf-8-sig") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()

                if not linea:
                    continue

                # Ignorar líneas que no comienzan con "|"
                if not linea.startswith("|"):
                    continue

                # Solamente procesar filas cuyo primer campo sea un número.
                # Esto permite ignorar encabezados y separadores tipo markdown.
                if not re.match(r"^\|\s*\d+\s*\|", linea):
                    continue

                # Separar columnas
                partes = [parte.strip() for parte in linea.split("|")]

                if partes and partes[0] == "":
                    partes.pop(0)

                if partes and partes[-1] == "":
                    partes.pop()

                # FORMATO 1: |id|nombre|descripcion|precio|stock|imagen|categoria_id|
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

                # FORMATO 2: |id|nombre|descripcion|precio|creado_en|
                # actualizado_en|categoria_id|imagen|stock|
                # (creado_en y actualizado_en NO se utilizan)
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

                # Convertir datos
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

                # Guardar producto (no se descartan duplicados; cada fila del
                # TXT es un producto).
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
    # CLAVE COMPLETA DEL PRODUCTO
    # =====================================================
    def obtener_clave_producto(self, producto):
        """
        Devuelve una representación completa del producto.

        A diferencia del seed anterior, el STOCK sí forma parte de la
        comparación. Esto permite diferenciar filas como:
            Producto A - stock 200
            Producto A - stock 300
        aunque el resto de los campos sea igual.

        El ID original tampoco forma parte de esta clave porque no
        determina el ID de Django.
        """
        return (
            producto["nombre"],
            producto["descripcion"],
            producto["precio"],
            producto["stock"],
            producto["imagen"],
            producto["categoria_id"],
        )

    # =====================================================
    # PRODUCTO DESDE MODELO
    # =====================================================
    def obtener_datos_producto_bd(self, producto):
        """
        Convierte un objeto Producto de Django a la misma estructura
        utilizada para comparar con el TXT.
        """
        return {
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": producto.precio,
            "stock": producto.stock,
            "imagen": producto.imagen.name if producto.imagen else None,
            "categoria_id": producto.categoria_id,
        }

    # =====================================================
    # VERIFICAR PRODUCTOS YA CARGADOS
    # =====================================================
    def obtener_productos_existentes_en_orden(self):
        """
        Devuelve los productos de la BD en orden de ID.

        El orden es importante porque el seed trabaja de manera
        incremental: los primeros N productos del TXT deben coincidir
        exactamente con los N productos ya cargados en la BD.
        Los IDs de Django no necesitan coincidir con los IDs originales
        del TXT.
        """
        return list(Producto.objects.all().order_by("id"))

    # =====================================================
    # DETERMINAR PRODUCTOS NUEVOS
    # =====================================================
    def determinar_productos_nuevos(self, productos_archivo, productos_bd):
        """
        Determina qué productos del TXT todavía no fueron cargados.

        Se utiliza una estrategia de PREFIJO: se comparan los primeros
        N productos del TXT contra los N productos de la BD. Si coinciden
        exactamente, se consideran ya cargados y se devuelve el resto.

        Esto permite agregar productos al final del TXT sin insertar
        duplicados al ejecutar nuevamente el seed.
        """
        cantidad_bd = len(productos_bd)
        cantidad_txt = len(productos_archivo)

        # BD vacía
        if cantidad_bd == 0:
            return productos_archivo

        # La BD tiene más productos que el TXT
        if cantidad_bd > cantidad_txt:
            raise CommandError(
                "La base de datos contiene más productos que productos.txt.\n\n"
                f"Productos en BD : {cantidad_bd}\n"
                f"Productos en TXT: {cantidad_txt}\n\n"
                "No se realizará ninguna inserción para evitar inconsistencias."
            )

        # Verificar que los productos existentes sean exactamente
        # el prefijo del TXT.
        for indice in range(cantidad_bd):
            producto_txt = productos_archivo[indice]
            producto_bd = productos_bd[indice]

            clave_txt = self.obtener_clave_producto(producto_txt)
            datos_bd = self.obtener_datos_producto_bd(producto_bd)
            clave_bd = self.obtener_clave_producto(datos_bd)

            if clave_txt != clave_bd:
                imagen_bd = producto_bd.imagen.name if producto_bd.imagen else None
                raise CommandError(
                    "\nSe detectó una diferencia entre productos.txt y la "
                    "base de datos.\n\n"
                    f"Posición: {indice + 1}\n"
                    f"ID BD: {producto_bd.id}\n"
                    f"ID original TXT: {producto_txt['id_original']}\n\n"
                    "Producto TXT:\n"
                    f"  Nombre      : {producto_txt['nombre']}\n"
                    f"  Descripción : {producto_txt['descripcion']}\n"
                    f"  Precio      : {producto_txt['precio']}\n"
                    f"  Stock       : {producto_txt['stock']}\n"
                    f"  Imagen      : {producto_txt['imagen']}\n"
                    f"  Categoría   : {producto_txt['categoria_id']}\n\n"
                    "Producto BD:\n"
                    f"  Nombre      : {producto_bd.nombre}\n"
                    f"  Descripción : {producto_bd.descripcion}\n"
                    f"  Precio      : {producto_bd.precio}\n"
                    f"  Stock       : {producto_bd.stock}\n"
                    f"  Imagen      : {imagen_bd}\n"
                    f"  Categoría   : {producto_bd.categoria_id}\n\n"
                    "El seed se detuvo para evitar duplicaciones.\n\n"
                    "Si modificaste productos que ya estaban cargados, debes "
                    "revisar la base de datos antes de volver a ejecutar el seed."
                )

        # Los productos existentes coinciden; todo lo que viene
        # después es nuevo.
        return productos_archivo[cantidad_bd:]

    # =====================================================
    # ACTUALIZAR SECUENCIA SQLITE
    # =====================================================
    def actualizar_secuencia(self):
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

                # Si sqlite_sequence todavía no tiene la fila, se inserta.
                if cursor.rowcount == 0:
                    cursor.execute(
                        "INSERT INTO sqlite_sequence (name, seq) "
                        "VALUES ('productos_producto', %s)",
                        [max_id],
                    )
            else:
                # No hay productos
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = 'productos_producto'"
                )

    # =====================================================
    # VERIFICAR CATEGORÍAS
    # =====================================================
    def verificar_categorias(self, productos):
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
        Convierte las filas del TXT en objetos Producto.
        No establece el ID; Django lo generará automáticamente.
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

        # LEER TXT
        self.stdout.write("")
        self.stdout.write("Leyendo productos.txt...")
        productos_archivo = self.obtener_filas(ruta)
        self.stdout.write(f"Productos encontrados en archivo: {len(productos_archivo)}")

        if not productos_archivo:
            self.stdout.write(
                self.style.WARNING("No se encontraron productos para cargar.")
            )
            return

        # VERIFICAR CATEGORÍAS
        self.stdout.write("")
        self.stdout.write("Verificando categorías...")
        self.verificar_categorias(productos_archivo)

        # OBTENER PRODUCTOS DE BD
        productos_bd = self.obtener_productos_existentes_en_orden()
        cantidad_bd = len(productos_bd)

        # DETERMINAR PRODUCTOS NUEVOS
        self.stdout.write("")
        self.stdout.write("Comparando productos existentes...")
        productos_nuevos = self.determinar_productos_nuevos(productos_archivo, productos_bd)
        cantidad_nuevos = len(productos_nuevos)

        # RESUMEN
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Productos en TXT      : {len(productos_archivo)}")
        self.stdout.write(f"Productos en BD       : {cantidad_bd}")
        self.stdout.write(f"Productos ya cargados : {cantidad_bd}")
        self.stdout.write(f"Productos a insertar  : {cantidad_nuevos}")
        self.stdout.write("=" * 60)

        # TODO YA ESTÁ CARGADO
        if not productos_nuevos:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los productos de productos.txt ya están cargados "
                    "en la base de datos."
                )
            )
            self.stdout.write(f"Total de productos: {cantidad_bd}")

            fin = time.perf_counter()
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos")
            )
            return

        # CREAR OBJETOS
        objetos_productos = self.crear_objetos_productos(productos_nuevos)

        # INSERTAR
        self.stdout.write("")
        self.stdout.write("Insertando productos...")

        with transaction.atomic():
            Producto.objects.bulk_create(objetos_productos, batch_size=500)
            self.actualizar_secuencia()

        # RESULTADOS
        fin = time.perf_counter()
        primer_id = Producto.objects.order_by("id").values_list("id", flat=True).first()
        ultimo_id = Producto.objects.order_by("-id").values_list("id", flat=True).first()
        total_bd = Producto.objects.count()

        # INFORMACIÓN FINAL
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Productos insertados correctamente: {cantidad_nuevos}")
        )
        self.stdout.write(f"Total productos en TXT: {len(productos_archivo)}")
        self.stdout.write(f"Total productos en BD: {total_bd}")
        self.stdout.write(f"Primer ID actual: {primer_id}")
        self.stdout.write(f"Último ID actual: {ultimo_id}")

        # VALIDACIÓN FINAL
        if total_bd == len(productos_archivo):
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "VALIDACIÓN CORRECTA: la cantidad de productos en la BD "
                    "coincide exactamente con productos.txt."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "ADVERTENCIA: la cantidad de productos en la BD todavía "
                    "no coincide con productos.txt."
                )
            )

        # TIEMPO
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos"))