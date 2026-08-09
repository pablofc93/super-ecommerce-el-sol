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
# 🔥 FUNCIÓN REUTILIZABLE
# =====================================================

def guardar_reporte(tipo, data, user):

    hace_un_minuto = now() - timedelta(minutes=1)

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
# 💰 INGRESOS POR CLIENTE
# =====================================================

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

        data = [

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

            for item in queryset

        ]

        paginator = PageNumberPagination()

        paginator.page_size = 5

        page = paginator.paginate_queryset(
            data,
            request
        )

        serializer = IngresosPorClienteSerializer(
            page,
            many=True
        )

        guardar_reporte(
            'ventas',
            data,
            request.user
        )

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

        serializer = ReporteHistoricoSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# =====================================================
# 🔥 REGISTRAR ACCESO
# =====================================================

class RegistrarAccesoView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        tipo = request.data.get('tipo')

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

            tipo=tipo,

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