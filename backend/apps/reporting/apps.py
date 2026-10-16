from django.apps import AppConfig


class ReportingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # tipo de campo utilizado por defecto para claves primarias
    name = 'apps.reporting' # nomhre de la app dentro del proyecto
    verbose_name = 'Reporting y Dashboard' # nombre descriptivo mostrado en interfaces administrativas
