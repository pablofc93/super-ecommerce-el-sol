"""
Comando para cargar productos desde utils/seed/productos.txt.

Uso:
    python manage.py seed_productos

Características:
- Lee todos los registros de productos.txt.
- Cada fila de producto representa un registro independiente.
- NO utiliza el ID original del TXT como ID de Django.
- NO elimina duplicados.
- NO compara productos por nombre, precio, stock, imagen, etc.
- Permite que existan productos idénticos.
- Solamente permite ejecutar el seed UNA VEZ.
- Si productos_producto ya contiene registros, no inserta nada.
- Detecta filas de productos de 7 o 9 columnas.
- Ignora únicamente encabezados y separadores Markdown.
- Informa exactamente las líneas problemáticas.
- Verifica las categorías antes de insertar.
- Utiliza bulk_create().
- Actualiza sqlite_sequence.
- Verifica al finalizar que la cantidad de registros de la BD
  coincida exactamente con la cantidad de registros del TXT.

IMPORTANTE:
Cada fila del TXT es considerada un producto independiente.

Por ejemplo:
    TXT:
        producto A
        producto A
        producto A

    Resultado:
        3 registros en productos_producto.

Los productos pueden tener exactamente los mismos datos.
"""

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

        # Formato argentino con coma decimal
        if "," in valor:
            # 4.143,39 -> 4143,39 -> 4143.39
            valor = valor.replace(".", "").replace(",", ".")

        # Formato sin coma
        else:
            partes = valor.split(".")
            # 4.143 -> 4143 | 7.900 -> 7900
            if len(partes) == 2 and len(partes[1]) == 3:
                valor = "".join(partes)

        try:
            return Decimal(valor).quantize(Decimal("0.01"))
        except InvalidOperation as error:
            raise ValueError(f"Precio inválido: '{valor}'") from error

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
        valor = str(valor).strip()

        if not valor:
            raise ValueError("El stock está vacío.")

        # Elimina separadores de miles.
        valor = valor.replace(".", "")

        try:
            stock = int(valor)
        except ValueError as error:
            raise ValueError(f"Stock inválido: '{valor}'") from error

        if stock < 0:
            raise ValueError(f"El stock no puede ser negativo: {stock}")

        return stock

    # =====================================================
    # DETERMINAR SI ES SEPARADOR MARKDOWN
    # =====================================================
    def es_separador_markdown(self, linea):
        """
        Determina si una línea corresponde al separador de una tabla
        Markdown. Ejemplo: |---|---|---|---|
        """
        contenido = linea.strip()

        if not contenido.startswith("|"):
            return False

        partes = [parte.strip() for parte in contenido.split("|")]

        for parte in partes:
            if parte == "":
                continue
            if set(parte) <= {"-", ":"}:
                continue
            return False

        return True

    # =====================================================
    # ES FILA DE PRODUCTO
    # =====================================================
    def es_fila_producto(self, linea):
        """
        Determina si una línea puede representar un producto.

        NO se exige que el ID original sea numérico, porque el ID
        original del TXT NO determina el ID de Django.

        Se consideran posibles productos las filas con 7 o 9 columnas.
        """
        linea = linea.strip()

        if not linea:
            return False

        if not linea.startswith("|"):
            return False

        if self.es_separador_markdown(linea):
            return False

        partes = [parte.strip() for parte in linea.split("|")]

        if partes and partes[0] == "":
            partes.pop(0)

        if partes and partes[-1] == "":
            partes.pop()

        return len(partes) in (7, 9)

    # =====================================================
    # OBTENER FILAS
    # =====================================================
    def obtener_filas(self, ruta):
        """
        Lee productos.txt.

        Cada fila válida de 7 o 9 columnas se considera un producto
        independiente. NO se eliminan duplicados, NO se compara el
        producto con otros productos, NO se utiliza el ID original
        para determinar si una fila debe insertarse.

        Devuelve una tupla:
            (productos, lineas_ignoradas, lineas_problematicas)
        """
        productos = []
        lineas_ignoradas = []
        lineas_problematicas = []

        with ruta.open("r", encoding="utf-8-sig") as archivo:
            for numero_linea, linea_original in enumerate(archivo, start=1):
                linea = linea_original.strip()

                # Línea vacía
                if not linea:
                    lineas_ignoradas.append((numero_linea, "Línea vacía"))
                    continue

                # Línea que no comienza con "|"
                if not linea.startswith("|"):
                    lineas_ignoradas.append((numero_linea, "No comienza con '|'"))
                    continue

                # Separador Markdown
                if self.es_separador_markdown(linea):
                    lineas_ignoradas.append((numero_linea, "Separador Markdown"))
                    continue

                # Separar columnas
                partes = [parte.strip() for parte in linea.split("|")]

                if partes and partes[0] == "":
                    partes.pop(0)

                if partes and partes[-1] == "":
                    partes.pop()

                cantidad_columnas = len(partes)

                # Encabezado
                if cantidad_columnas in (7, 9) and partes[0].lower() == "id":
                    lineas_ignoradas.append((numero_linea, "Encabezado de tabla"))
                    continue

                # Cualquier otra cantidad de columnas
                if cantidad_columnas not in (7, 9):
                    lineas_problematicas.append({
                        "linea": numero_linea,
                        "contenido": linea_original.rstrip("\n"),
                        "motivo": (
                            f"Cantidad de columnas inválida: {cantidad_columnas}. "
                            f"Se esperaban 7 o 9."
                        ),
                    })
                    continue

                # FORMATO 1 (7 columnas)
                if cantidad_columnas == 7:
                    (
                        id_original,
                        nombre,
                        descripcion,
                        precio,
                        stock,
                        imagen,
                        categoria_id,
                    ) = partes

                # FORMATO 2 (9 columnas)
                else:
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

                # ID ORIGINAL: no se utiliza como ID de Django, por lo
                # tanto no es necesario que sea numérico. Se conserva
                # solo como información del TXT.
                id_original = id_original.strip()

                # NOMBRE: si está vacío, se informa el problema (no se
                # descarta silenciosamente).
                nombre = nombre.strip()

                if not nombre:
                    lineas_problematicas.append({
                        "linea": numero_linea,
                        "contenido": linea_original.rstrip("\n"),
                        "motivo": "El nombre está vacío.",
                    })
                    continue

                # DESCRIPCIÓN
                descripcion = descripcion if descripcion else None

                # PRECIO
                try:
                    precio_convertido = self.convertir_precio(precio)
                except ValueError as error:
                    lineas_problematicas.append({
                        "linea": numero_linea,
                        "contenido": linea_original.rstrip("\n"),
                        "motivo": str(error),
                    })
                    continue

                # STOCK
                try:
                    stock_convertido = self.convertir_stock(stock)
                except ValueError as error:
                    lineas_problematicas.append({
                        "linea": numero_linea,
                        "contenido": linea_original.rstrip("\n"),
                        "motivo": str(error),
                    })
                    continue

                # CATEGORÍA
                try:
                    categoria_id = int(str(categoria_id).strip())
                except ValueError:
                    lineas_problematicas.append({
                        "linea": numero_linea,
                        "contenido": linea_original.rstrip("\n"),
                        "motivo": f"categoria_id inválido: '{categoria_id}'.",
                    })
                    continue

                # IMAGEN
                imagen = imagen if imagen else None

                # AGREGAR PRODUCTO
                productos.append({
                    "numero_linea": numero_linea,
                    "id_original": id_original,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio_convertido,
                    "stock": stock_convertido,
                    "imagen": imagen,
                    "categoria_id": categoria_id,
                })

        return productos, lineas_ignoradas, lineas_problematicas

    # =====================================================
    # MOSTRAR DIAGNÓSTICO
    # =====================================================
    def mostrar_diagnostico(self, lineas_ignoradas, lineas_problematicas):
        """
        Muestra información de diagnóstico para saber exactamente qué
        ocurrió durante la lectura del TXT.
        """
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("DIAGNÓSTICO DE LECTURA")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Líneas ignoradas     : {len(lineas_ignoradas)}")
        self.stdout.write(f"Líneas problemáticas  : {len(lineas_problematicas)}")

        if lineas_ignoradas:
            self.stdout.write("")
            self.stdout.write("Líneas ignoradas:")
            for numero_linea, motivo in lineas_ignoradas:
                self.stdout.write(f"  Línea {numero_linea}: {motivo}")

        if lineas_problematicas:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("LÍNEAS PROBLEMÁTICAS:"))
            for problema in lineas_problematicas:
                self.stdout.write(self.style.ERROR(f"\n  Línea {problema['linea']}"))
                self.stdout.write(f"  Motivo: {problema['motivo']}")
                self.stdout.write(f"  Contenido: {problema['contenido']}")

        self.stdout.write("")
        self.stdout.write("=" * 60)

    # =====================================================
    # VERIFICAR CATEGORÍAS
    # =====================================================
    def verificar_categorias(self, productos):
        """Verifica que todas las categorías utilizadas por los productos existan."""
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
                "No existen las siguientes categorías en productos_categoria:\n"
                f"{sorted(categorias_faltantes)}"
            )

    # =====================================================
    # CREAR OBJETOS PRODUCTO
    # =====================================================
    def crear_objetos_productos(self, productos):
        """
        Convierte TODAS las filas del TXT en objetos Producto. No
        elimina duplicados, no utiliza sets, no compara productos ni
        establece el ID.
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
        """Actualiza sqlite_sequence para productos_producto."""
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
            else:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = 'productos_producto'"
                )

    # =====================================================
    # VALIDAR CANTIDAD FINAL
    # =====================================================
    def validar_cantidad_final(self, cantidad_esperada, cantidad_insertada):
        """
        Verifica que:
            cantidad TXT = cantidad insertada = cantidad BD
        """
        cantidad_bd = Producto.objects.count()

        if cantidad_insertada != cantidad_esperada:
            raise CommandError(
                "\nERROR DE VALIDACIÓN.\n\n"
                f"Productos esperados : {cantidad_esperada}\n"
                f"Productos preparados: {cantidad_insertada}\n\n"
                "No se insertaron todos los productos."
            )

        if cantidad_bd != cantidad_esperada:
            raise CommandError(
                "\nERROR DE VALIDACIÓN.\n\n"
                f"Productos esperados : {cantidad_esperada}\n"
                f"Productos en BD     : {cantidad_bd}\n\n"
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
        self.stdout.write("=" * 70)
        self.stdout.write("CARGADOR DE PRODUCTOS")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Archivo: {ruta}")
        self.stdout.write("=" * 70)

        # VERIFICAR ARCHIVO
        if not ruta.exists():
            raise CommandError(f"No se encontró el archivo:\n{ruta}")

        # VERIFICAR SI YA FUE EJECUTADO
        cantidad_bd_actual = Producto.objects.count()

        if cantidad_bd_actual > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("EL SEED DE PRODUCTOS YA FUE EJECUTADO.")
            )
            self.stdout.write("")
            self.stdout.write(f"Productos actualmente en BD: {cantidad_bd_actual}")
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("No se realizará ninguna inserción.")
            )
            self.stdout.write(
                self.style.WARNING("Este seed solamente puede ejecutarse una vez.")
            )
            return

        # LEER TXT
        self.stdout.write("")
        self.stdout.write("Leyendo productos.txt...")

        productos_archivo, lineas_ignoradas, lineas_problematicas = self.obtener_filas(ruta)
        cantidad_productos = len(productos_archivo)

        # DIAGNÓSTICO
        self.mostrar_diagnostico(lineas_ignoradas, lineas_problematicas)

        # RESUMEN DE LECTURA
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("RESUMEN DE LECTURA")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Productos detectados : {cantidad_productos}")
        self.stdout.write(f"Líneas ignoradas     : {len(lineas_ignoradas)}")
        self.stdout.write(f"Líneas problemáticas : {len(lineas_problematicas)}")
        self.stdout.write("=" * 70)

        # SI HAY PROBLEMAS
        if lineas_problematicas:
            raise CommandError(
                "\nEl TXT contiene filas que parecen ser productos pero "
                "tienen datos inválidos.\n\n"
                f"Productos válidos detectados: {cantidad_productos}\n"
                f"Filas problemáticas: {len(lineas_problematicas)}\n\n"
                "Revisa las líneas indicadas en el diagnóstico anterior.\n"
                "El seed NO realizará ninguna inserción parcial."
            )

        # VERIFICAR PRODUCTOS
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
        cantidad_objetos = len(objetos_productos)
        self.stdout.write(f"Productos preparados: {cantidad_objetos}")

        # VERIFICACIÓN ANTES DE INSERTAR
        if cantidad_objetos != cantidad_productos:
            raise CommandError(
                "\nERROR INTERNO DEL SEED.\n\n"
                f"Productos detectados: {cantidad_productos}\n"
                f"Objetos preparados: {cantidad_objetos}\n\n"
                "La cantidad no coincide. No se realizará la inserción."
            )

        # INSERTAR
        self.stdout.write("")
        self.stdout.write("Insertando productos...")

        with transaction.atomic():
            Producto.objects.bulk_create(objetos_productos, batch_size=500)
            self.actualizar_secuencia()

        # VALIDACIÓN FINAL
        total_bd = self.validar_cantidad_final(cantidad_productos, cantidad_objetos)

        # OBTENER IDS
        primer_id = Producto.objects.order_by("id").values_list("id", flat=True).first()
        ultimo_id = Producto.objects.order_by("-id").values_list("id", flat=True).first()

        # TIEMPO
        fin = time.perf_counter()

        # RESULTADO FINAL
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("CARGA COMPLETADA CORRECTAMENTE"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Registros encontrados en TXT : {cantidad_productos}")
        self.stdout.write(f"Registros preparados         : {cantidad_objetos}")
        self.stdout.write(f"Registros insertados en BD   : {total_bd}")
        self.stdout.write(f"Primer ID generado           : {primer_id}")
        self.stdout.write(f"Último ID generado           : {ultimo_id}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("VALIDACIÓN CORRECTA:"))
        self.stdout.write(
            self.style.SUCCESS(
                "La cantidad de registros del TXT coincide exactamente con "
                "la cantidad de registros de productos_producto."
            )
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Tiempo total: {fin - inicio:.2f} segundos"))