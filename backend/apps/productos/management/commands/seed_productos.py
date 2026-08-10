"""
Comando para cargar productos desde utils/seed/productos.txt.

Uso:

python manage.py seed_productos

Características:

- Lee los productos desde utils/seed/productos.txt.
- No utiliza los IDs originales del archivo.
- Si la tabla está vacía, los IDs comienzan en 1.
- No inserta productos duplicados.
- Conserva nombre, descripción, precio, stock, imagen y categoría.
- Convierte correctamente precios con formato argentino.
- Utiliza bulk_create() para realizar la carga rápidamente.
- Actualiza sqlite_sequence cuando corresponde.
"""

from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.utils import timezone

from apps.productos.models import Producto


class Command(BaseCommand):

    help = "Carga productos desde utils/seed/productos.txt."

    # =====================================================
    # RUTA DEL ARCHIVO
    # =====================================================

    def obtener_ruta_archivo(self):
        """
        Devuelve la ruta absoluta del archivo productos.txt.
        """

        return (
            Path(__file__).resolve().parents[4]
            / "utils"
            / "seed"
            / "productos.txt"
        )

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
            raise ValueError(
                "El precio está vacío."
            )

        valor = (
            valor
            .replace("$", "")
            .replace(" ", "")
        )

        if "," in valor:

            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

        else:

            partes = valor.split(".")

            if (
                len(partes) == 2
                and len(partes[1]) == 3
            ):
                valor = "".join(partes)

        try:

            return Decimal(valor).quantize(
                Decimal("0.01")
            )

        except InvalidOperation as error:

            raise ValueError(
                f"Precio inválido: {valor}"
            ) from error

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

        valor = (
            str(valor)
            .strip()
            .replace(".", "")
        )

        if not valor:

            raise ValueError(
                "El stock está vacío."
            )

        try:

            stock = int(valor)

        except ValueError as error:

            raise ValueError(
                f"Stock inválido: {valor}"
            ) from error

        if stock < 0:

            raise ValueError(
                f"El stock no puede ser negativo: {stock}"
            )

        return stock

    # =====================================================
    # OBTENER FILAS
    # =====================================================

    def obtener_filas(self, ruta):
        """
        Lee productos.txt y devuelve los productos válidos.

        El archivo utiliza este formato:

        |id|nombre|descripcion|precio|stock|imagen|categoria_id|
        """

        productos = []

        with ruta.open(
            "r",
            encoding="utf-8-sig"
        ) as archivo:

            for numero_linea, linea in enumerate(
                archivo,
                start=1
            ):

                linea = linea.strip()

                if not linea:
                    continue

                if not linea.startswith("|"):
                    continue

                if not re.match(
                    r"^\|\s*\d+\s*\|",
                    linea
                ):
                    continue

                partes = [
                    parte.strip()
                    for parte in linea.split("|")
                ]

                if partes and partes[0] == "":
                    partes.pop(0)

                if partes and partes[-1] == "":
                    partes.pop()

                if len(partes) != 7:

                    raise CommandError(
                        f"Línea {numero_linea}: "
                        f"se esperaban 7 columnas y se encontraron "
                        f"{len(partes)}."
                    )

                (
                    id_original,
                    nombre,
                    descripcion,
                    precio,
                    stock,
                    imagen,
                    categoria_id
                ) = partes

                try:

                    id_original = int(
                        id_original
                    )

                    precio_convertido = (
                        self.convertir_precio(
                            precio
                        )
                    )

                    stock_convertido = (
                        self.convertir_stock(
                            stock
                        )
                    )

                    categoria_id = int(
                        categoria_id
                    )

                except (
                    ValueError,
                    TypeError
                ) as error:

                    raise CommandError(
                        f"Error en línea {numero_linea}: "
                        f"{error}"
                    ) from error

                if not nombre:

                    raise CommandError(
                        f"Línea {numero_linea}: "
                        "el nombre del producto está vacío."
                    )

                productos.append({
                    "id_original": id_original,
                    "nombre": nombre,
                    "descripcion": descripcion or None,
                    "precio": precio_convertido,
                    "stock": stock_convertido,
                    "imagen": imagen or None,
                    "categoria_id": categoria_id,
                })

        return productos

    # =====================================================
    # CLAVE DEL PRODUCTO
    # =====================================================

    def obtener_clave_producto(self, producto):
        """
        Devuelve una clave utilizada para determinar
        si un producto ya existe.

        No se utiliza el ID porque el ID del TXT no debe
        determinar el ID de la base de datos.

        El stock se excluye de la clave porque puede cambiar
        posteriormente como consecuencia de ventas.
        """

        return (
            producto["nombre"],
            producto["descripcion"],
            producto["precio"],
            producto["imagen"],
            producto["categoria_id"],
        )

    # =====================================================
    # PRODUCTOS EXISTENTES
    # =====================================================

    def obtener_productos_existentes(self):
        """
        Devuelve las claves de los productos que ya existen
        en la base de datos.
        """

        existentes = set()

        productos = (
            Producto.objects
            .all()
            .values(
                "nombre",
                "descripcion",
                "precio",
                "imagen",
                "categoria_id",
            )
        )

        for producto in productos:

            existentes.add(
                self.obtener_clave_producto(
                    producto
                )
            )

        return existentes

    # =====================================================
    # ACTUALIZAR SECUENCIA SQLITE
    # =====================================================

    def actualizar_secuencia(self):
        """
        Actualiza sqlite_sequence para productos_producto.

        SQLite mantiene las secuencias de los modelos con
        AUTOINCREMENT en la tabla sqlite_sequence.

        No se utiliza ON CONFLICT porque dependiendo de la
        versión/configuración de SQLite, la columna name de
        sqlite_sequence no puede utilizarse como objetivo
        de una cláusula ON CONFLICT.

        Se realiza primero UPDATE y, si no existe la fila,
        se realiza INSERT.
        """

        if connection.vendor != "sqlite":
            return

        with connection.cursor() as cursor:

            # ---------------------------------------------
            # Obtener ID máximo
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT MAX(id)
                FROM productos_producto
                """
            )

            resultado = cursor.fetchone()

            max_id = (
                resultado[0]
                if resultado and resultado[0] is not None
                else None
            )

            # ---------------------------------------------
            # Si existen productos
            # ---------------------------------------------

            if max_id is not None:

                cursor.execute(
                    """
                    UPDATE sqlite_sequence
                    SET seq = %s
                    WHERE name = 'productos_producto'
                    """,
                    [max_id]
                )

                filas_actualizadas = cursor.rowcount

                # -----------------------------------------
                # Si no existía la fila, crearla
                # -----------------------------------------

                if filas_actualizadas == 0:

                    cursor.execute(
                        """
                        INSERT INTO sqlite_sequence
                        (name, seq)
                        VALUES
                        ('productos_producto', %s)
                        """,
                        [max_id]
                    )

            # ---------------------------------------------
            # Si no existen productos
            # ---------------------------------------------

            else:

                cursor.execute(
                    """
                    DELETE FROM sqlite_sequence
                    WHERE name = 'productos_producto'
                    """
                )

    # =====================================================
    # VERIFICAR CATEGORÍAS
    # =====================================================

    def verificar_categorias(self, productos):
        """
        Verifica que todas las categorías utilizadas por los
        productos existan antes de realizar la carga.

        No crea ni modifica categorías.
        """

        categoria_ids = {
            producto["categoria_id"]
            for producto in productos
            if producto["categoria_id"] is not None
        }

        if not categoria_ids:
            return

        placeholders = ",".join(
            ["%s"] * len(categoria_ids)
        )

        with connection.cursor() as cursor:

            cursor.execute(
                f"""
                SELECT id
                FROM productos_categoria
                WHERE id IN ({placeholders})
                """,
                list(categoria_ids)
            )

            categorias_existentes = {
                fila[0]
                for fila in cursor.fetchall()
            }

        categorias_faltantes = (
            categoria_ids
            - categorias_existentes
        )

        if categorias_faltantes:

            raise CommandError(
                "No existen las siguientes categorías "
                "en productos_categoria: "
                f"{sorted(categorias_faltantes)}"
            )

    # =====================================================
    # PROCESO PRINCIPAL
    # =====================================================

    def handle(self, *args, **options):

        inicio = time.perf_counter()

        ruta = self.obtener_ruta_archivo()

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            "CARGADOR DE PRODUCTOS"
        )
        self.stdout.write("=" * 60)
        self.stdout.write(
            f"Archivo: {ruta}"
        )
        self.stdout.write("=" * 60)

        # =================================================
        # VERIFICAR ARCHIVO
        # =================================================

        if not ruta.exists():

            raise CommandError(
                f"No se encontró el archivo:\n{ruta}"
            )

        # =================================================
        # LEER PRODUCTOS
        # =================================================

        self.stdout.write("")
        self.stdout.write(
            "Leyendo productos.txt..."
        )

        productos_archivo = (
            self.obtener_filas(ruta)
        )

        self.stdout.write(
            f"Productos encontrados en archivo: "
            f"{len(productos_archivo)}"
        )

        if not productos_archivo:

            self.stdout.write(
                self.style.WARNING(
                    "No se encontraron productos para cargar."
                )
            )

            return

        # =================================================
        # VERIFICAR CATEGORÍAS
        # =================================================

        self.stdout.write("")
        self.stdout.write(
            "Verificando categorías..."
        )

        self.verificar_categorias(
            productos_archivo
        )

        # =================================================
        # OBTENER PRODUCTOS EXISTENTES
        # =================================================

        existentes = (
            self.obtener_productos_existentes()
        )

        productos_nuevos = []

        claves_procesadas = set()

        # =================================================
        # DETERMINAR PRODUCTOS NUEVOS
        # =================================================

        ahora = timezone.now()

        for producto in productos_archivo:

            clave = (
                self.obtener_clave_producto(
                    producto
                )
            )

            # ---------------------------------------------
            # Ya existe en la base
            # ---------------------------------------------

            if clave in existentes:
                continue

            # ---------------------------------------------
            # Producto repetido dentro del TXT
            # ---------------------------------------------

            if clave in claves_procesadas:
                continue

            # ---------------------------------------------
            # Crear objeto
            # ---------------------------------------------

            productos_nuevos.append(
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
            )

            claves_procesadas.add(clave)

        # =================================================
        # RESUMEN PREVIO
        # =================================================

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            f"Productos encontrados : "
            f"{len(productos_archivo)}"
        )
        self.stdout.write(
            f"Productos existentes  : "
            f"{len(existentes)}"
        )
        self.stdout.write(
            f"Productos a insertar  : "
            f"{len(productos_nuevos)}"
        )
        self.stdout.write("=" * 60)

        # =================================================
        # NO HAY PRODUCTOS NUEVOS
        # =================================================

        if not productos_nuevos:

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los productos ya existen. "
                    "No se insertaron duplicados."
                )
            )

            return

        # =================================================
        # COMPROBAR SI LA TABLA ESTABA VACÍA
        # =================================================

        tabla_vacia = not Producto.objects.exists()

        # =================================================
        # INSERTAR PRODUCTOS
        # =================================================

        self.stdout.write("")
        self.stdout.write(
            "Insertando productos..."
        )

        with transaction.atomic():

            Producto.objects.bulk_create(
                productos_nuevos,
                batch_size=500
            )

            # ---------------------------------------------
            # Actualizar secuencia SQLite
            # ---------------------------------------------

            self.actualizar_secuencia()

        # =================================================
        # FIN
        # =================================================

        fin = time.perf_counter()

        primer_id = (
            Producto.objects
            .order_by("id")
            .values_list(
                "id",
                flat=True
            )
            .first()
        )

        ultimo_id = (
            Producto.objects
            .order_by("-id")
            .values_list(
                "id",
                flat=True
            )
            .first()
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Productos insertados correctamente: "
                f"{len(productos_nuevos)}"
            )
        )

        if tabla_vacia:

            self.stdout.write(
                self.style.SUCCESS(
                    "La tabla estaba vacía: "
                    "los IDs fueron generados desde 1."
                )
            )

        self.stdout.write(
            f"Primer ID actual: {primer_id}"
        )

        self.stdout.write(
            f"Último ID actual: {ultimo_id}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Tiempo total: "
                f"{fin - inicio:.2f} segundos"
            )
        )