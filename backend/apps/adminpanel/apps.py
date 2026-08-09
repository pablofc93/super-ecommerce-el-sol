from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.adminpanel'

    def ready(self):
        import apps.adminpanel.signals
