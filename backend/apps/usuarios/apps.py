from django.apps import AppConfig

#se crea la clase UsuariosConfig que hereda de la clase AppConfig de Django, 
# que permite configurar la aplicación "usuarios" dentro del proyecto Django.
class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
