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
    page_size = 5 # cada página tendrá como máximo 5 resultados


# =====================================================
# DASHBOARD ANALÍTICO
# =====================================================
class DashboardAnaliticoView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "productos_analizados": ProductoMasVendido.objects.count(), #se representan la cantidad de registros
            "categorias_analizadas": CategoriaMasMovida.objects.count(),
            "clientes_segmentados": ClienteSegmentado.objects.count(),
            "reglas_asociacion": ReglaAsociacion.objects.count(),
        }

        return Response(data) # transforma el diccionario en un objeto JSON y lo devuelve como respuesta a la solicitud GET


# =====================================================
# PRODUCTOS MÁS VENDIDOS (HISTÓRICO)
# =====================================================
class ProductosMasVendidosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = ProductoMasVendido.objects.all().order_by('-fecha_calculo') # obtener todos los productos más vendidos, ordenados por fecha de cálculo descendente 
        paginator = StandardResultsSetPagination() # se crea una instancia del paginador personalizado
        result_page = paginator.paginate_queryset(queryset, request) # se aplica la paginación al queryset, obteniendo solo los resultados de la página actual
        serializer = ProductoMasVendidoSerializer(result_page, many=True) # se envían los resultados paginados al serializer para convertirlos a JSON
        guardar_reporte('analitica', serializer.data, request.user) # se devuelven los datos serializados en la respuesta, junto con la información de paginación

        return paginator.get_paginated_response(serializer.data)


# =====================================================
# CATEGORÍAS MÁS MOVIDAS - obtiene las 10 categorías con mayor movimiento de productos, ordenadas de mayor a menor
# =====================================================
class CategoriasMasMovidasAgrupadasView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            CategoriaMasMovida.objects
            .values('categoria_id', 'nombre_categoria') # indica con que campos se trabajarán
            .annotate(total_movimiento=Sum('total_movimiento')) # con esto se agrupa por categoría y se calcula el total de movimiento para cada una
            .order_by('-total_movimiento')[:10]
        )

        return Response(data)


# =====================================================
# CLIENTES SEGMENTADOS - continuar aqui
# =====================================================
class ClientesSegmentadosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = ClienteSegmentado.objects.all() #a lmacena un objeto queryset con todos los registros de la tabla ClienteSegmentado
        resultado = [] # lista para almacenar resultados
        for cs in queryset: # recorrer cada registro de cliente segmentado
            usuario = cs.cliente
            pedidos = Pedido.objects.filter(
                cliente__id_cliente=usuario, # pedidos -> cliente.id_cliente = usuario.id_cliente
                estado__in=['pagado', 'enviado', 'entregado']
            )
            # suma todos los pedidos de cada cliente y si no hay pedidos, asigna 0 a la variable total_gasto
            total_gasto = pedidos.aggregate(total=Sum('total'))['total'] or 0
            total_pedidos = pedidos.count()

            # append es para agregar el diccionario creado al final de la lista resultado
            resultado.append({
                "cliente": usuario.id,
                "cluster": cs.cluster,
                "total_gasto": float(total_gasto),
                "total_pedidos": total_pedidos,
            })

        # se devuelve la lista resultado como respuesta a la solicitud GET, en formato JSON
        # para que pueda ser interpretada por el frontend
        return Response(resultado)


# =====================================================
# REGLAS DE ASOCIACIÓN
# obtener las reglas de asociación generadas por el algoritmo Apriori, ordenadas por confianza de mayor a menor
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
            productos_ids = regla.productos # se obtiene los id de los productos que están en el campo productos
            productos = Producto.objects.filter(
                id__in=productos_ids # buscar los productos cuyo id esté en la lista de productos_ids ej: productos_ids = [1, 3, 7]
            )

            nombres = list(
                productos.values_list(
                    'nombre',
                    flat=True # devuelve una lista simple con los nombres de los productos, en lugar de una lista de tuplas
                )
            )

            #verificar que la lista nombres tenga al menos 2 elementos antes de agregar la regla al resultado
            if len(nombres) >= 2:
                # se construye el resultado
                resultado.append({
                    "base": nombres[0],
                    "recomendado": nombres[1],
                    "soporte": regla.soporte,
                    "confianza": regla.confianza,
                    "lift": regla.lift,
                })

        # se crea el paginador personalizado configurado anteriormente
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset( # muestra los resultados de la página actual, según la configuración del paginador
            resultado,
            request
        )

        # se llama a la función guardar_reporte que recibe como parámetros 3 argumentos
        guardar_reporte(
            "recomendacion", # indica el tipo de categoría del reporte
            result_page, # información de la página actual del resultado
            request.user # el usuario que generó el reporte
        )

        #devuelve al frontend los resultados paginados en formato JSON, 
        # junto con la información de paginación (número de página, total de páginas, etc.)
        return paginator.get_paginated_response(result_page)


# =====================================================
# PRODUCTOS MÁS VENDIDOS AGRUPADOS
# obtiene los productos más vendidos agrupados por producto, ordenados de mayor a menor según la cantidad total vendida
# =====================================================
class ProductosMasVendidosAgrupadosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            ProductoMasVendido.objects
            .values( # equivale al group by en SQL, se agrupa por producto_id y nombre_producto
                'producto_id',
                'nombre_producto'
            )
            .annotate(
                total_vendido=Sum('total_vendido')
            )
            .order_by('-total_vendido')[:10] #ordenar por total vendido en orden descendente y limitar a los 10 primeros resultados
        )

        return Response(data)


# =====================================================
# DEMANDA POR MES
# devuelve la cantidad de unidades de productos vendidas por mes, agrupadas por categoría de producto
# =====================================================
class DemandaPorMesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = demanda_por_periodo(periodo='mes') # calcula la demanda agrupándola por mes, el resultado se guarda en data
        return Response(data) # luego se devuelve el resultado de esa operación para ser consumido por el frontend, en formato JSON


# =====================================================
# INGRESOS POR MES
# se obtienen los ingresos totales por mes, considerando solo los pedidos que están en estado 'pagado', 'enviado' o 'entregado'
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
            .exclude(fecha__isnull=True) # se excluyen los pedidos que no tienen fecha, para evitar errores al extraer el mes posteriormente
            .annotate( # annotate es para agregar un campo calculado a cada registro del queryset, en este caso se extrae el mes de la fecha del pedido
                mes=ExtractMonth('fecha')
            )
            .values('mes') # agrupa los resultados por mes, para que se pueda calcular el total de ingresos por cada mes
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
            if item["mes"] is not None # indica que solamente se incluirán los registros que tengan un valor de mes distino de None
        ]

        return Response(resultado) # devuelve la lista resultado como respuesta a la solicitud GET, en formato JSON, para el front


# =====================================================
# KPIs POR PROVINCIA
# =====================================================
class KpisPorProvinciaView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            Cliente.objects
            .values('provincia')
            .annotate( # annotate agrega un campo calculado a cada registro denominado cantidad_clientes
                cantidad_clientes=Count('id_cliente')
            )
            .order_by('-cantidad_clientes')
        )

        resultado = []

        # se recorren todos los registros de la consulta anterior, para calcular los KPIs por provincia
        for item in data:
            provincia = item['provincia'] # extrae el valor de la provincia del registro actual ej: item[Jujuy]
            pedidos = Pedido.objects.filter(
                cliente__provincia=provincia,
                estado__in=[
                    'pagado',
                    'enviado',
                    'entregado'
                ]
            )

            # se calcula el total de ventas de los pedidos 
            # filtrados por provincia, si no hay pedidos, se asigna 0 a ventas_totales
            # agregate agrega el total de ventas de los pedidos filtrados por provincia, si no hay pedidos, se asigna 0 a ventas_totales
            # a diferencia de annotate, aggregate devuelve un unico resultado
            ventas_totales = pedidos.aggregate(
                total=Sum('total')
            )['total'] or 0

            cantidad_clientes = item['cantidad_clientes']

            #ticket promedio es el gasto promedio por cliente
            ticket_promedio = 0

            if cantidad_clientes > 0:
                ticket_promedio = (
                    float(ventas_totales)
                    / cantidad_clientes
                )

            # append agrega un diccionario con los KPIs calculados para la provincia actual a la lista resultado
            # agrega un resultado al final de la lista resultado
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
        # ranking es una variable que almacena el resultado de una consulta a la base de datos, 
        # que obtiene los 10 productos más vendidos, ordenados de mayor a menor según la cantidad total vendida
        ranking = (
            ProductoMasVendido.objects
            .values('producto_id') # se obtienen los id de los productos más vendidos
            .annotate(
                total_vendido=Sum('total_vendido') # se agrega un campo calculado que suma la cantidad total vendida de cada producto
            )
            .order_by('-total_vendido')[:10]
        )

        # se recorre la variable ranking y se extraen los id de 
        # los productos más vendidos, que se almacenan 
        # en la lista ids_productos
        ids_productos = [
            item["producto_id"]
            for item in ranking
        ]

        #luego se buscan los productos cuyo id esté en la lista ids_productos,
        productos = Producto.objects.filter(
            id__in=ids_productos
        )

        # se ordenan según el orden de los ids en la lista ids_productos
        productos_ordenados = sorted(
            productos,
            key=lambda p: ids_productos.index(p.id)
        )

        serializer = ProductoSerializer(
            productos_ordenados,
            many=True, # indica que se van a serializar múltiples objetos, en este caso, la lista de productos ordenados
            context={"request": request} # se pasa el contexto de la solicitud al serializer, para que pueda generar URLs completas para los campos de imagen o archivo
        )

        return Response(serializer.data)