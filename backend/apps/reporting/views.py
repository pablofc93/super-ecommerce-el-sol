from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.usuarios.permissions import IsAdminUser

from django.db.models import Sum
from django.utils.timezone import now, localtime

from datetime import timedelta
from decimal import Decimal

from .models import ReporteHistorico

from .serializers import (
    DashboardSerializer,
    ReporteHistoricoSerializer,
    IngresosPorClienteSerializer
)

from apps.productos.models import Producto, Categoria
from apps.clientes.models import Cliente

from apps.analitica.models import (
    ProductoMasVendido,
    CategoriaMasMovida,
    ClienteSegmentado
)

from apps.pedidos.models import Pedido


# =====================================================
# Guarda un reporte histórico, pero evitando que se guarde el mismo
# tipo de reporte repetidamente durante un período de 1 minuto
# =====================================================
def guardar_reporte(tipo, data, user):
    hace_un_minuto = now() - timedelta(minutes=1) # se calcula la fecha y hora de hace exactamente 1 minuto

    #se busca si ya existe un reporte 
    existe = ReporteHistorico.objects.filter(
        tipo=tipo,
        generado_por=user,
        fecha_generacion__gte=hace_un_minuto
    ).exists()

    if not existe:
        ReporteHistorico.objects.create(
            tipo=tipo,
            data=data,
            generado_por=user
        )


# =====================================================
# 📊 DASHBOARD
# =====================================================

class DashboardView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):

        # ================= KPIs =================
        total_productos = Producto.objects.count()
        total_categorias = Categoria.objects.count()
        total_clientes = Cliente.objects.count()
        total_pedidos = Pedido.objects.count()
        ventas_totales = (
            Pedido.objects
            .filter(
                estado__in=[
                    'pagado',
                    'enviado',
                    'entregado'
                ]
            )
            .aggregate(total=Sum('total'))['total']
            or 0
        )

        if isinstance(ventas_totales, Decimal):
            ventas_totales = float(ventas_totales)

        # ================= CATEGORÍAS ACTIVAS =================

        categorias_activas = (
            CategoriaMasMovida.objects
            .values('categoria_id')
            .distinct()
            .count()
        )

        # ================= PRODUCTO MÁS VENDIDO =================

        producto = (
            ProductoMasVendido.objects
            .order_by(
                '-fecha_calculo',
                '-total_vendido'
            )
            .first()
        )

        producto_data = {
            "producto": (
                producto.nombre_producto
                if producto else "N/A"
            ),
            "cantidad": (
                producto.total_vendido
                if producto else 0
            )
        }

        # ================= CATEGORÍA MÁS MOVIDA =================

        categoria = (
            CategoriaMasMovida.objects
            .order_by(
                '-fecha_calculo',
                '-total_movimiento'
            )
            .first()
        )

        categoria_nombre = (
            categoria.nombre_categoria
            if categoria else "N/A"
        )

        # ================= CLIENTES SEGMENTADOS =================

        clusters = (
            ClienteSegmentado.objects
            .values('cluster')
            .annotate(
                cantidad_clientes=Sum(1)
            )
            .order_by('cluster')
        )

        dashboard_data = {

            # 🔵 KPIs
            "total_productos": total_productos,
            "total_categorias": total_categorias,
            "categorias_activas": categorias_activas,
            "total_clientes": total_clientes,
            "total_pedidos": total_pedidos,
            "ventas_totales": ventas_totales,

            # 🟣 ANALÍTICA
            "producto_mas_vendido": producto_data,
            "categoria_mas_movida": categoria_nombre,
            "clientes_segmentados": list(clusters)
        }

        return Response(dashboard_data)


# =====================================================
# 💰 INGRESOS POR CLIENTE - hasta aqui
# =====================================================
# el objetivo es obtener cuánto dinero generó cada cliente a partir
# de sus pedidos, ordenar los clientes desde el que generó más ingresos
# hasta el que generó menos, paginar los resultados y devolverlos mediante
# la API
class IngresosPorClienteView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        queryset = (
            Pedido.objects
            .filter(
                estado__in=[
                    'pagado',
                    'enviado',
                    'entregado'
                ]
            )
            .values(
                'cliente',
                'cliente__id_cliente__username',
                'cliente__id_cliente__email'
            )
            .annotate(
                total_ingresos=Sum('total')
            )
            .order_by('-total_ingresos')
        )

        data = [ # hasta aqui
            {
                "cliente": item["cliente"],
                "cliente_nombre": item[
                    "cliente__id_cliente__username"
                ],
                "cliente_email": item[
                    "cliente__id_cliente__email"
                ],
                "total_ingresos": float(
                    item["total_ingresos"] or 0
                )
            }
            for item in queryset # este es un for que recorre uno por uno los items de la variable queryset
        ]

        paginator = PageNumberPagination()
        paginator.page_size = 5

        #obtener la página solicitada
        page = paginator.paginate_queryset(
            data, # contiene todos los resultados
            request # contiene información sobre la página que está solicitando el frontend
        )

        serializer = IngresosPorClienteSerializer(
            page,
            many=True
        )

        guardar_reporte(
            'ventas', # tipo de reporte
            data, # información del reporte
            request.user # usuario que generó el reporte
        )

        # aquí ya devuelve la respuesta pero con la paginación aplicada
        return paginator.get_paginated_response(
            serializer.data
        )


# =====================================================
# 🕓 REPORTES HISTÓRICOS
# =====================================================

class ReportesHistoricosView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        tipos_permitidos = [
            'dashboard',
            'usuarios',
            'productos',
            'pedidos',
            'reportes',
            'ventas'
        ]

        queryset = (
            ReporteHistorico.objects
            .filter(tipo__in=tipos_permitidos)
            .order_by('-fecha_generacion')
        )

        paginator = PageNumberPagination()
        paginator.page_size = 5
        page = paginator.paginate_queryset(
            queryset,
            request
        )

        # se envian los registros de la pagina actual para serializar
        serializer = ReporteHistoricoSerializer(
            page,
            many=True
        )

        # se devuelven los datos ya serializados de la pagina actual
        return paginator.get_paginated_response(
            serializer.data
        )


# =====================================================
# 🔥 REGISTRAR ACCESO
# =====================================================
# se registra cuándo un usuario accede a determinadas secciones del sistema

class RegistrarAccesoView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        tipo = request.data.get('tipo') # obtiene el valor de tipo enviado por el Frontend
        tipos_validos = [
            'dashboard',
            'usuarios',
            'productos',
            'pedidos',
            'reportes',
            'ventas'
        ]

        if tipo not in tipos_validos:
            return Response(
                {
                    "error": "Tipo de acceso inválido"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ReporteHistorico.objects.create(
            tipo=tipo, # guardar en el campo tipo de ReporteHistorico el valor recibido desde el frontend
            generado_por=request.user,
            data={
                "mensaje": f"Acceso registrado a {tipo}",
                "fecha": localtime().isoformat()
            }
        )

        return Response(
            {
                "message": "Acceso registrado correctamente"
            },
            status=status.HTTP_201_CREATED
        )