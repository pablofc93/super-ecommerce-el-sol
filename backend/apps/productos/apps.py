# Este archivo contiene la configuración principal de la aplicación Productos.
# Su función es definir cómo Django debe identificar y cargar esta aplicación,
# además de ejecutar determinadas acciones cuando la aplicación está completamente preparada.
from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productos"

    # este método se ejecuta cuando la aplicación fue cargada y está lista para utilizarse
    # luego de cargar importa las signals de productos
    def ready(self):
        import apps.productos.signals