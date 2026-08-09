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
    path('api/auth/', include('apps.usuarios.urls')),

    # =========================
    # ECOMMERCE
    # =========================
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/productos/', include('apps.productos.urls')),
    path('api/pedidos/', include('apps.pedidos.urls')),

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
