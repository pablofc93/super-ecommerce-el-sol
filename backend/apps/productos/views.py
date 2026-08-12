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

    queryset = Producto.objects.all().order_by("-id")
    serializer_class = ProductoSerializer

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
    @action(detail=False, methods=['get'])
    def mas_vendidos(self, request):

        productos_ids = (
            PedidoItem.objects
            .filter(pedido__estado__in=['pagado', 'enviado', 'entregado'])
            .values('producto')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')[:10]
        )

        ids = [p['producto'] for p in productos_ids]

        productos = Producto.objects.filter(id__in=ids)

        # Mantener el orden por ventas
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

        total_productos = Producto.objects.count()
        total_stock = sum(p.stock for p in Producto.objects.all())

        return Response({
            "total_productos": total_productos,
            "total_stock": total_stock
        })


# =========================
# Compras del cliente
# =========================
class CompraViewSet(viewsets.ModelViewSet):

    serializer_class = CompraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Compra.objects.all()

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.cliente)


# =========================
# Categorías
# =========================
class CategoriaViewSet(viewsets.ModelViewSet):

    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre"]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):

        if request.query_params.get("all") == "true":

            categorias = self.get_queryset()

            serializer = self.get_serializer(
                categorias,
                many=True
            )

            return Response(serializer.data)

        return super().list(request, *args, **kwargs)