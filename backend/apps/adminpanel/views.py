from django.http import JsonResponse # permite devolver una respuesta HTTP en formato JSON
from django.utils.timezone import now
from datetime import timedelta

from apps.reporting.models import ReporteHistorico # se importa el modelo ReporteHistorico que pertenece a la app reporting

# tipo indica qué módulo del panel administrativo se está accediendo (dashboard, productos, usuarios, pedidos, reportes)
# user indica qué usuario está generando el reporte (request.user)
def guardar_reporte(tipo, user):
    hace_un_minuto = now() - timedelta(minutes=1) #se calcula el tiempo actual menos un minuto para filtrar los reportes generados en el último minuto

    #busca en la base de datos reportes que cumplan con los siguientes criterios:
    # tipo: el tipo de reporte que se está generando (dashboard, productos, usuarios, pedidos, reportes)
    # generado_por: el usuario que está generando el reporte (request.user)
    # fecha_generacion__gte: la fecha de generación del reporte debe ser mayor o igual a hace_un_minuto (es decir, en el último minuto)
    existe = ReporteHistorico.objects.filter(
        tipo=tipo,
        generado_por=user,
        fecha_generacion__gte=hace_un_minuto #significa "buscar reportes cuya fecha de generación sea mayor o igual a hace_un_minuto"
    ).exists()

    # si no existe un registro de reporte con los criterios anteriores, se crea un nuevo registro 
    # en la base de datos con el tipo de reporte, los datos del módulo y el usuario que lo generó (si está autenticado)
    if not existe:
        ReporteHistorico.objects.create(
            tipo=tipo,
            data={"modulo": tipo},
            generado_por=user if user.is_authenticated else None
        )


# 📊 registro acceso: Dashboard
# Este método se ejecuta cuando el administrador accede al endpoint asociado
# al dashboard. Su función es registrar el acceso al dashboard en la base de datos 
# y devolver una respuesta JSON con un mensaje.
def dashboard(request):
    guardar_reporte('dashboard', request.user)
    return JsonResponse({"message": "Dashboard del panel administrativo"})


# 🔐 registro acceso: Login
def login_admin(request):
    return JsonResponse({"message": "Login del administrador"})


# 📦 registro acceso: Productos
def admin_productos_lista(request):
    guardar_reporte('productos', request.user)
    return JsonResponse({"message": "Listado de productos (admin)"})


def admin_productos_agregar(request):
    return JsonResponse({"message": "Agregar un nuevo producto (admin)"})


def admin_productos_editar(request, id):
    return JsonResponse({"message": f"Editar producto con ID {id} (admin)"})


# 👥 registro acceso: Usuarios
def admin_usuarios_lista(request):
    guardar_reporte('usuarios', request.user)
    return JsonResponse({"message": "Listado de usuarios (admin)"})


def admin_usuarios_agregar(request):
    return JsonResponse({"message": "Agregar usuario (admin)"})


def admin_usuarios_editar(request, id):
    return JsonResponse({"message": f"Editar usuario con ID {id} (admin)"})


# 🧾 registro acceso: Pedidos
def admin_pedidos_lista(request):
    guardar_reporte('pedidos', request.user)
    return JsonResponse({"message": "Listado de pedidos (admin)"})


def admin_pedido_detalle(request, id):
    return JsonResponse({"message": f"Detalle del pedido con ID {id} (admin)"})


# 👤 registro acceso: Perfil
def admin_perfil(request):
    return JsonResponse({"message": "Perfil del administrador"})


# 📑 registro acceso: Reportes
def admin_reportes(request):
    guardar_reporte('reportes', request.user)
    return JsonResponse({"message": "Reportes administrativos"})