from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================
    # ADMIN DJANGO
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # AUTH / USUARIOS
    # =========================
    path('api/auth/', include('apps.usuarios.urls')), # ese endpoint maneja las solicitudes de login, logout y registro de usuarios. Recibe la solicitud y la dirige a las urls de la app de usuarios 

    # =========================
    # ECOMMERCE
    # =========================
    path('api/clientes/', include('apps.clientes.urls')), # CLIENTES
    path('api/productos/', include('apps.productos.urls')), # PRODUCTOS
    path('api/pedidos/', include('apps.pedidos.urls')), # PEDIDOS

    # =========================
    # RECOMENDACIÓN (✅ CORREGIDO)
    # =========================
    path('api/recomendacion/', include('apps.recomendacion.urls')),

    # =========================
    # ADMIN PANEL Y ANALÍTICA
    # =========================
    path('api/adminpanel/', include('apps.adminpanel.urls')),
    path('api/analitica/', include('apps.analitica.urls')),

    # =========================
    # REPORTING
    # ========================
    path('api/reporting/', include('apps.reporting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
