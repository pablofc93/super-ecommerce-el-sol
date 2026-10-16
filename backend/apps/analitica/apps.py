# apps/analitica/apps.py
from django.apps import AppConfig

class AnaliticaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # indica que tipo de campo automático utilizará Django como clave primaria cuando un modelo no lo especifique
    name = 'apps.analitica' # indica el nombre de la aplicación y su ubicación
    verbose_name = 'Analítica y Minería de Datos' # nombre legible para usuarios que se verá en el panel administrativo y otros lugares del sistema donde se requiera

