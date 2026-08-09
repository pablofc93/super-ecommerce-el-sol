from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CompraViewSet, CategoriaViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'compras', CompraViewSet, basename='compra')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

urlpatterns = [
    path('', include(router.urls)),
]
