# apps/analitica/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .services.demanda import demanda_por_periodo
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from apps.reporting.views import guardar_reporte
from apps.productos.models import Producto
from apps.productos.serializers import ProductoSerializer
from apps.pedidos.models import Pedido
from .services.apriori import calcular_reglas_asociacion
from django.db.models.functions import ExtractMonth
from django.db.models import Count, Sum
from apps.clientes.models import Cliente


from .models import (
    ProductoMasVendido,
    CategoriaMasMovida,
    ClienteSegmentado,
    ReglaAsociacion
)

from .serializers import (
    ProductoMasVendidoSerializer,
    CategoriaMasMovidaSerializer,
    ClienteSegmentadoSerializer,
    ReglaAsociacionSerializer
)


# =====================================================
# 🔥 PAGINADOR PERSONALIZADO (REUTILIZABLE)
# =====================================================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5


# =====================================================
# DASHBOARD ANALÍTICO
# =====================================================
class DashboardAnaliticoView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "productos_analizados": ProductoMasVendido.objects.count(),
            "categorias_analizadas": CategoriaMasMovida.objects.count(),
            "clientes_segmentados": ClienteSegmentado.objects.count(),
            "reglas_asociacion": ReglaAsociacion.objects.count(),
        }
        return Response(data)


# =====================================================
# PRODUCTOS MÁS VENDIDOS (HISTÓRICO)
# =====================================================
class ProductosMasVendidosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = ProductoMasVendido.objects.all().order_by('-fecha_calculo')

        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = ProductoMasVendidoSerializer(result_page, many=True)

        guardar_reporte('analitica', serializer.data, request.user)

        return paginator.get_paginated_response(serializer.data)


# =====================================================
# CATEGORÍAS MÁS MOVIDAS
# =====================================================
class CategoriasMasMovidasAgrupadasView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            CategoriaMasMovida.objects
            .values('categoria_id', 'nombre_categoria')
            .annotate(total_movimiento=Sum('total_movimiento'))
            .order_by('-total_movimiento')[:10]
        )

        return Response(data)


# =====================================================
# CLIENTES SEGMENTADOS
# =====================================================
class ClientesSegmentadosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = ClienteSegmentado.objects.all()

        resultado = []

        for cs in queryset:

            usuario = cs.cliente

            pedidos = Pedido.objects.filter(
                cliente__id_cliente=usuario,
                estado__in=['pagado', 'enviado', 'entregado']
            )

            total_gasto = pedidos.aggregate(total=Sum('total'))['total'] or 0
            total_pedidos = pedidos.count()

            resultado.append({
                "cliente": usuario.id,
                "cluster": cs.cluster,
                "total_gasto": float(total_gasto),
                "total_pedidos": total_pedidos,
            })

        return Response(resultado)


# =====================================================
# REGLAS DE ASOCIACIÓN
# =====================================================
class ReglasAsociacionView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        reglas = (
            ReglaAsociacion.objects
            .all()
            .order_by('-confianza')
        )

        resultado = []

        for regla in reglas:

            productos_ids = regla.productos

            productos = Producto.objects.filter(
                id__in=productos_ids
            )

            nombres = list(
                productos.values_list(
                    'nombre',
                    flat=True
                )
            )

            if len(nombres) >= 2:

                resultado.append({
                    "base": nombres[0],
                    "recomendado": nombres[1],
                    "soporte": regla.soporte,
                    "confianza": regla.confianza,
                    "lift": regla.lift,
                })

        paginator = StandardResultsSetPagination()

        result_page = paginator.paginate_queryset(
            resultado,
            request
        )

        guardar_reporte(
            "recomendacion",
            result_page,
            request.user
        )

        return paginator.get_paginated_response(
            result_page
        )


# =====================================================
# PRODUCTOS MÁS VENDIDOS AGRUPADOS
# =====================================================
class ProductosMasVendidosAgrupadosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            ProductoMasVendido.objects
            .values(
                'producto_id',
                'nombre_producto'
            )
            .annotate(
                total_vendido=Sum('total_vendido')
            )
            .order_by('-total_vendido')[:10]
        )

        return Response(data)


# =====================================================
# DEMANDA POR MES
# =====================================================
class DemandaPorMesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = demanda_por_periodo(periodo='mes')
        return Response(data)


# =====================================================
# INGRESOS POR MES
# =====================================================
class VentasPorMesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            Pedido.objects
            .filter(
                estado__in=[
                    'pagado',
                    'enviado',
                    'entregado'
                ]
            )
            .exclude(fecha__isnull=True)
            .annotate(
                mes=ExtractMonth('fecha')
            )
            .values('mes')
            .annotate(
                total_ingresos=Sum('total')
            )
            .order_by('mes')
        )

        resultado = [
            {
                "mes": item["mes"],
                "total_ingresos": float(item["total_ingresos"] or 0)
            }
            for item in data
            if item["mes"] is not None
        ]

        return Response(resultado)


# =====================================================
# KPIs POR PROVINCIA
# =====================================================
class KpisPorProvinciaView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            Cliente.objects
            .values('provincia')
            .annotate(
                cantidad_clientes=Count('id_cliente')
            )
            .order_by('-cantidad_clientes')
        )

        resultado = []

        for item in data:

            provincia = item['provincia']

            pedidos = Pedido.objects.filter(
                cliente__provincia=provincia,
                estado__in=[
                    'pagado',
                    'enviado',
                    'entregado'
                ]
            )

            ventas_totales = pedidos.aggregate(
                total=Sum('total')
            )['total'] or 0

            cantidad_clientes = item['cantidad_clientes']

            ticket_promedio = 0

            if cantidad_clientes > 0:
                ticket_promedio = (
                    float(ventas_totales)
                    / cantidad_clientes
                )

            resultado.append({
                "provincia": provincia or "Sin provincia",
                "cantidad_clientes": cantidad_clientes,
                "ventas_totales": float(ventas_totales),
                "ticket_promedio": round(ticket_promedio, 2)
            })

        return Response(resultado)


# =====================================================
# PRODUCTOS MÁS VENDIDOS (PÚBLICO)
# =====================================================
class ProductosMasVendidosPublicView(APIView):
    permission_classes = []

    def get(self, request):

        ranking = (
            ProductoMasVendido.objects
            .values('producto_id')
            .annotate(
                total_vendido=Sum('total_vendido')
            )
            .order_by('-total_vendido')[:10]
        )

        ids_productos = [
            item["producto_id"]
            for item in ranking
        ]

        productos = Producto.objects.filter(
            id__in=ids_productos
        )

        productos_ordenados = sorted(
            productos,
            key=lambda p: ids_productos.index(p.id)
        )

        serializer = ProductoSerializer(
            productos_ordenados,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)