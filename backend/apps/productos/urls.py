from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CompraViewSet, CategoriaViewSet

router = DefaultRouter() # objeto responsable de generar automáticamente las URLs para distintos ViewSet evitando declarar manualmente cada endpoint

router.register(r'productos', ProductoViewSet, basename='producto') #se registra ProductoViewSet bajo la ruta /productos
router.register(r'compras', CompraViewSet, basename='compra')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

#router.urls incorpora automáticamente todas las rutas creadas por DefaultRouter al sistema de URLs de Django
#de esta manera no es necesario crear individualmente cada endpoint correspondiente a productos, compras y categorías
urlpatterns = [
    path('', include(router.urls)),
]
