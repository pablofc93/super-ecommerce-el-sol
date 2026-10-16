# views.py cumple la función de recibir las solicitudes del frontend, procesarlas y devolver una respuesta.
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from .models import Categoria, Producto, Compra
from .serializers import CategoriaSerializer, ProductoSerializer, CompraSerializer
from apps.usuarios.permissions import IsAdminUser
from apps.pedidos.models import PedidoItem


# =========================
# Productos
# =========================
class ProductoViewSet(viewsets.ModelViewSet):

    queryset = Producto.objects.all().order_by("-id") #se obtienen todos los productos y se ordenan por id de forma decreciente
    serializer_class = ProductoSerializer #indica el serializer que se va a utilizar

    #esta configuración permite que el endpoint pueda recibir información mediante formularios y archivos
    #importante para el manejo de imágenes de productos
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria']
    search_fields = ['nombre', 'descripcion']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'mas_vendidos']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    # =========================
    # PRODUCTOS MÁS VENDIDOS (PÚBLICO)
    # =========================
    # decorador @action permite agregar un endpoint adicional a la vista diferente de las operaciones CRUD tradicionales 
    @action(detail=False, methods=['get'])
    def mas_vendidos(self, request):

        #equivalente a una consulta SQL a la base de datos
        #obtiene los productos que tuvieron mayor cantidad de unidades vendidas
        productos_ids = (
            PedidoItem.objects
            .filter(pedido__estado__in=['pagado', 'enviado', 'entregado'])
            .values('producto')
            .annotate(total_vendido=Sum('cantidad')) #calcula la suma de la cantidad vendida de cada producto
            .order_by('-total_vendido')[:10] #se ordenan los productos y se obtienen los 10 más vendidos
        )

        ids = [p['producto'] for p in productos_ids]

        #luego de obtener los ids de los prudctos más vendidos
        #se obtienen los productos completos
        productos = Producto.objects.filter(id__in=ids)

        # Mantener el orden por ventas luego de hacer la consulta al modelo Producto
        productos_dict = {p.id: p for p in productos}
        productos_ordenados = [
            productos_dict[i]
            for i in ids
            if i in productos_dict
        ]

        serializer = ProductoSerializer(
            productos_ordenados,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    # =========================
    # STATS ADMIN
    # =========================
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):

        total_productos = Producto.objects.count() #cuenta la cantidad de productos
        total_stock = sum(p.stock for p in Producto.objects.all()) #obtiene el total de productos en stock

        return Response({
            "total_productos": total_productos,
            "total_stock": total_stock
        })


# =========================
# Compras del cliente
# =========================
class CompraViewSet(viewsets.ModelViewSet):

    #serializer_calss es un atributo al cual se le asigna la clase CompraSerializer
    serializer_class = CompraSerializer #las compras serán procesadas mediante CompraSerializer
    permission_classes = [permissions.IsAuthenticated]

    #metodo que devuelve todas las compras existentes
    def get_queryset(self):
        return Compra.objects.all()

    #método que asocia la compra con el cliente autenticado
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.cliente)


# =========================
# Categorías - gestiona las operaciones CRUD correspondientes a las categorias de los productos
# =========================
class CategoriaViewSet(viewsets.ModelViewSet):

    queryset = Categoria.objects.all().order_by("nombre") #obtener todas las categorias y las ordena por nombre
    serializer_class = CategoriaSerializer #se determina que esta vista usará CategoriaSerializer como serializador

    filter_backends = [filters.SearchFilter] #búsqueda de categorías por nombre
    search_fields = ["nombre"]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']: #indica que el listado y ver una categoría específica son funciones públicas
            return [permissions.AllowAny()]

        return [IsAdminUser()]


    #devuelve el listado de categorias con su id 
    def list(self, request, *args, **kwargs):
        if request.query_params.get("all") == "true":
            categorias = self.get_queryset()
            serializer = self.get_serializer(
                categorias,
                many=True
            )
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)