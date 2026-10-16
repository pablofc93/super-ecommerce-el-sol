from django.apps import AppConfig


#esta clase hereda de AppConfig proporcionada por Django
#permite definir la configuración de la aplicación
class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #define el campo por defecto que usará el modelo para id (claves primarias), será BigautoField
    name = 'apps.clientes' #indica donde se encuentra la app de clientes

    #luego de cargar la aplicación se carga y se importan las señales
    #se cargan las signales aqui y no arriba para evitar errores
    def ready(self):
        import apps.clientes.signals