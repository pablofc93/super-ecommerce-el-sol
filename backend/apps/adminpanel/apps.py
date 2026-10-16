from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.adminpanel'

    #este método se ejecutar cuando la aplicación termina de cargarse
    #en este caso se importa el módulo signals para que se registren las señales definidas en él
    def ready(self):
        import apps.adminpanel.signals
