
from pathlib import Path
from contextlib import closing
import os
import shutil
import sqlite3
import sys
import tempfile

from mega import Mega


# =========================================================
# CONFIGURACIÓN
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

# Destino definitivo de la base de datos.
# Debe coincidir con DATABASES en settings.py.
DB_PATH = BASE_DIR / "db.sqlite3"

MEGA_URL = (
    "https://mega.nz/file/f5QBkZoZ"
    "#CxVA_bZ7eUmzYYwo_cSmCo29gdZZq1Q4KnJp20s4OMs"
)


# =========================================================
# VALIDACIÓN DE SQLITE
# =========================================================

def validar_base(db_path):
    """Comprueba la integridad de una base SQLite."""

    if not db_path.is_file() or db_path.stat().st_size == 0:
        return False

    try:
        uri = db_path.resolve().as_uri() + "?mode=ro"

        with closing(sqlite3.connect(uri, uri=True)) as connection:
            resultado = connection.execute(
                "PRAGMA quick_check"
            ).fetchone()

            if not resultado or resultado[0] != "ok":
                print(f"Integridad incorrecta: {db_path}")
                return False

            tablas = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            ).fetchall()

        print(f"Base válida: {db_path}")
        print(f"Tamaño: {db_path.stat().st_size:,} bytes")
        print(f"Cantidad de tablas: {len(tablas)}")
        print(f"Integridad SQLite: {resultado[0]}")

        return True

    except (sqlite3.Error, OSError) as error:
        print(f"Error al validar la base: {error}")
        return False


# =========================================================
# REEMPLAZO DE LA BASE
# =========================================================

def reemplazar_base(origen, destino):
    """Reemplaza el destino mediante una operación atómica."""

    try:
        os.replace(str(origen), str(destino))

    except PermissionError as error:
        raise PermissionError(
            f"No se pudo reemplazar '{destino}'.\n"
            "Alguno de los archivos podría estar ocupado."
        ) from error


# =========================================================
# PROCESO PRINCIPAL
# =========================================================

def main():
    forzar = "--forzar" in sys.argv

    # Conservar la base existente si es válida y no se fuerza
    # una actualización.
    if DB_PATH.exists() and not forzar:
        print("Ya existe una base de datos.")

        if validar_base(DB_PATH):
            print("Se conserva la copia existente.")
            return

        raise RuntimeError(
            "La base existente no es válida. "
            "Revisá el archivo antes de continuar con --forzar."
        )

    print("Iniciando descarga desde MEGA...")

    # El archivo intermedio se crea junto a la base definitiva
    # para permitir el reemplazo dentro del mismo sistema de archivos.
    archivo_nuevo = BASE_DIR / "db_nuevo.sqlite3"

    with tempfile.TemporaryDirectory(
        prefix="descarga_mega_"
    ) as temp_dir:

        carpeta_temporal = Path(temp_dir)
        descargada = carpeta_temporal / "db.sqlite3"

        mega = Mega()

        try:
            mega.login()

            mega.download_url(
                MEGA_URL,
                str(carpeta_temporal),
                "db.sqlite3",
            )

        finally:
            mega._http.close()

        if not validar_base(descargada):
            raise RuntimeError(
                "La descarga no produjo una base SQLite válida."
            )

        try:
            shutil.copy2(descargada, archivo_nuevo)

            if not validar_base(archivo_nuevo):
                raise RuntimeError(
                    "La copia intermedia no superó la validación."
                )

            reemplazar_base(archivo_nuevo, DB_PATH)

        finally:
            if archivo_nuevo.exists():
                try:
                    archivo_nuevo.unlink()
                except OSError as error:
                    print(
                        "Aviso: no se pudo eliminar el archivo intermedio:",
                        archivo_nuevo,
                    )
                    print(f"Motivo: {error}")

    print("Descarga finalizada correctamente.")
    validar_base(DB_PATH)


if __name__ == "__main__":
    main()
