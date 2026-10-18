
from pathlib import Path, PurePosixPath
from contextlib import closing
import shutil
import stat
import sys
import tempfile
import zipfile

from mega import Mega


# =========================================================
# CONFIGURACIÓN
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
#BASE_DIR = Path(__file__).resolve().parent

# Debe coincidir con MEDIA_ROOT de settings.py.
MEDIA_ROOT = BASE_DIR / "media"
#MEDIA_ROOT = BASE_DIR / "prueba_mega_imagenes"

# Directorio donde se instalarán las imágenes de productos.
DESTINO_IMAGENES = MEDIA_ROOT / "productos"
#DESTINO_IMAGENES = MEDIA_ROOT / "productos"

MEGA_URL = (
    "https://mega.nz/file/O4Bx2QiB"
    "#JPVPSTEs3aFXRX2qe1DMybnsP9zHJ9k7AU1gS9Z-_q8"
)

NOMBRE_ZIP = "productos.zip"

EXTENSIONES_IMAGEN = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".gif", ".bmp", ".avif", ".svg"
}


# =========================================================
# VALIDACIÓN Y EXTRACCIÓN DEL ZIP
# =========================================================

def validar_zip(ruta_zip):
    """Comprueba la integridad del ZIP y que contenga imágenes."""

    if not ruta_zip.is_file() or ruta_zip.stat().st_size == 0:
        raise RuntimeError("El archivo ZIP no existe o está vacío.")

    try:
        with zipfile.ZipFile(ruta_zip, "r") as archivo_zip:
            error = archivo_zip.testzip()

            if error is not None:
                raise RuntimeError(
                    f"El ZIP contiene un archivo dañado: {error}"
                )

            archivos = [
                info for info in archivo_zip.infolist()
                if not info.is_dir()
            ]

            # Evita archivos con rutas que puedan escapar del destino.
            for info in archivos:
                nombre = info.filename.replace("\\", "/")
                ruta = PurePosixPath(nombre)

                if (
                    ruta.is_absolute()
                    or ".." in ruta.parts
                    or (
                        ruta.parts
                        and ":" in ruta.parts[0]
                    )
                ):
                    raise RuntimeError(
                        f"Ruta no permitida dentro del ZIP: {nombre}"
                    )

                # No se permiten enlaces simbólicos.
                tipo = info.external_attr >> 16
                if stat.S_ISLNK(tipo):
                    raise RuntimeError(
                        f"El ZIP contiene un enlace simbólico: {nombre}"
                    )

            imagenes = [
                info for info in archivos
                if Path(info.filename).suffix.lower()
                in EXTENSIONES_IMAGEN
            ]

            if not imagenes:
                raise RuntimeError(
                    "El ZIP no contiene imágenes reconocidas."
                )

            print(f"ZIP válido: {ruta_zip}")
            print(f"Archivos incluidos: {len(archivos)}")
            print(f"Imágenes encontradas: {len(imagenes)}")

            return len(imagenes)

    except zipfile.BadZipFile as error:
        raise RuntimeError(
            "El archivo descargado no es un ZIP válido."
        ) from error


def extraer_zip(ruta_zip, directorio_extraccion):
    """Extrae el ZIP después de comprobar sus rutas."""

    with zipfile.ZipFile(ruta_zip, "r") as archivo_zip:
        archivo_zip.extractall(directorio_extraccion)

    # Si el ZIP contiene una carpeta raíz llamada productos,
    # instala su contenido, no una carpeta productos anidada.
    carpeta_productos = directorio_extraccion / "productos"

    if carpeta_productos.is_dir():
        return carpeta_productos

    return directorio_extraccion


# =========================================================
# INSTALACIÓN SEGURA
# =========================================================

def instalar_imagenes(carpeta_origen, carpeta_temporal):
    """
    Prepara la nueva carpeta y reemplaza la anterior.
    Si el reemplazo falla, intenta restaurar la anterior.
    """

    carpeta_nueva = carpeta_temporal / "productos_nuevos"
    carpeta_anterior = carpeta_temporal / "productos_anterior"

    shutil.copytree(carpeta_origen, carpeta_nueva)

    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

    respaldo_creado = False

    try:
        if DESTINO_IMAGENES.exists():
            DESTINO_IMAGENES.rename(carpeta_anterior)
            respaldo_creado = True

        carpeta_nueva.rename(DESTINO_IMAGENES)

    except OSError:
        # Si falla la instalación, intenta recuperar la carpeta previa.
        if respaldo_creado and carpeta_anterior.exists():
            if DESTINO_IMAGENES.exists():
                shutil.rmtree(DESTINO_IMAGENES)

            carpeta_anterior.rename(DESTINO_IMAGENES)

        raise

    print(f"Imágenes instaladas en: {DESTINO_IMAGENES}")


# =========================================================
# PROCESO PRINCIPAL
# =========================================================

def main():
    forzar = "--forzar" in sys.argv

    if DESTINO_IMAGENES.exists() and not forzar:
        imagenes_existentes = [
            archivo
            for archivo in DESTINO_IMAGENES.rglob("*")
            if archivo.is_file()
            and archivo.suffix.lower() in EXTENSIONES_IMAGEN
        ]

        if imagenes_existentes:
            print(
                f"Ya existen {len(imagenes_existentes)} imágenes en "
                f"{DESTINO_IMAGENES}"
            )
            print("No se descarga nuevamente.")
            print("Usá --forzar para actualizar las imágenes.")
            return

    print("Iniciando descarga de imágenes desde MEGA...")

    # El directorio temporal se crea dentro del backend para
    # mantener el reemplazo en el mismo sistema de archivos.
    with tempfile.TemporaryDirectory(
        prefix="descarga_imagenes_",
        dir=BASE_DIR
    ) as directorio_temporal:

        temporal = Path(directorio_temporal)
        ruta_zip = temporal / NOMBRE_ZIP
        directorio_extraccion = temporal / "extraidas"

        directorio_extraccion.mkdir()

        mega = Mega()

        try:
            mega.login()

            mega.download_url(
                MEGA_URL,
                str(temporal),
                NOMBRE_ZIP
            )

        finally:
            # Cierra la conexión HTTP de la biblioteca.
            with closing(mega._http):
                pass

        # La carpeta anterior no se modifica hasta que la
        # descarga y la validación del ZIP hayan terminado.
        validar_zip(ruta_zip)

        carpeta_origen = extraer_zip(
            ruta_zip,
            directorio_extraccion
        )

        imagenes_extraidas = [
            archivo
            for archivo in carpeta_origen.rglob("*")
            if archivo.is_file()
            and archivo.suffix.lower() in EXTENSIONES_IMAGEN
        ]

        if not imagenes_extraidas:
            raise RuntimeError(
                "No se encontraron imágenes después de extraer el ZIP."
            )

        instalar_imagenes(carpeta_origen, temporal)

    print("Descarga e instalación finalizadas correctamente.")

    # Comprueba el resultado final.
    imagenes_finales = [
        archivo
        for archivo in DESTINO_IMAGENES.rglob("*")
        if archivo.is_file()
        and archivo.suffix.lower() in EXTENSIONES_IMAGEN
    ]

    print(f"Total de imágenes instaladas: {len(imagenes_finales)}")


if __name__ == "__main__":
    main()
