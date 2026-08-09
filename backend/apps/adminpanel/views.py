from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

from apps.reporting.models import ReporteHistorico


def guardar_reporte(tipo, user):
    hace_un_minuto = now() - timedelta(minutes=1)

    existe = ReporteHistorico.objects.filter(
        tipo=tipo,
        generado_por=user,
        fecha_generacion__gte=hace_un_minuto
    ).exists()

    if not existe:
        ReporteHistorico.objects.create(
            tipo=tipo,
            data={"modulo": tipo},
            generado_por=user if user.is_authenticated else None
        )


# 📊 Dashboard
def dashboard(request):
    guardar_reporte('dashboard', request.user)
    return JsonResponse({"message": "Dashboard del panel administrativo"})


# 🔐 Login
def login_admin(request):
    return JsonResponse({"message": "Login del administrador"})


# 📦 Productos
def admin_productos_lista(request):
    guardar_reporte('productos', request.user)
    return JsonResponse({"message": "Listado de productos (admin)"})


def admin_productos_agregar(request):
    return JsonResponse({"message": "Agregar un nuevo producto (admin)"})


def admin_productos_editar(request, id):
    return JsonResponse({"message": f"Editar producto con ID {id} (admin)"})


# 👥 Usuarios
def admin_usuarios_lista(request):
    guardar_reporte('usuarios', request.user)
    return JsonResponse({"message": "Listado de usuarios (admin)"})


def admin_usuarios_agregar(request):
    return JsonResponse({"message": "Agregar usuario (admin)"})


def admin_usuarios_editar(request, id):
    return JsonResponse({"message": f"Editar usuario con ID {id} (admin)"})


# 🧾 Pedidos
def admin_pedidos_lista(request):
    guardar_reporte('pedidos', request.user)
    return JsonResponse({"message": "Listado de pedidos (admin)"})


def admin_pedido_detalle(request, id):
    return JsonResponse({"message": f"Detalle del pedido con ID {id} (admin)"})


# 👤 Perfil
def admin_perfil(request):
    return JsonResponse({"message": "Perfil del administrador"})


# 📑 Reportes
def admin_reportes(request):
    guardar_reporte('reportes', request.user)
    return JsonResponse({"message": "Reportes administrativos"})