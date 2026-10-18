
#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Descargar la base SQLite desde MEGA.
python download_db.py --forzar

# Descargar e instalar las imágenes de productos.
python download_images.py --forzar

# Recopilar los archivos estáticos.
python manage.py collectstatic --noinput
