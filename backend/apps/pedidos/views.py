# apps/pedidos/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from .models import Carrito, CarritoItem, Pedido, PedidoItem, Pago
from .serializers import CarritoSerializer, PedidoListSerializer
from apps.clientes.models import Cliente
from apps.productos.models import Producto


# =========================================================
# OBTENER O CREAR CLIENTE
# =========================================================

def obtener_o_crear_cliente(usuario):

    cliente, created = Cliente.objects.get_or_create(
        id_cliente=usuario
    )

    return cliente


# =========================================================
# OBTENER O CREAR CARRITO
# =========================================================

def obtener_o_crear_carrito(usuario):

    cliente = obtener_o_crear_cliente(usuario)

    carrito, created = Carrito.objects.get_or_create(
        cliente=cliente
    )

    if not carrito.activo:
        carrito.activo = True
        carrito.save()

    return carrito


# =========================================================
# VER CARRITO
# =========================================================

class CarritoView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        carrito = obtener_o_crear_carrito(request.user)

        serializer = CarritoSerializer(carrito)

        return Response(serializer.data)


# =========================================================
# AGREGAR PRODUCTO AL CARRITO
# =========================================================

class AgregarProductoCarritoView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        producto_id = request.data.get("producto_id")
        cantidad = request.data.get("cantidad", 1)

        if not producto_id:
            return Response({"error": "Falta producto_id"}, status=400)

        try:
            cantidad = int(cantidad)
        except ValueError:
            return Response({"error": "Cantidad inválida"}, status=400)

        if cantidad <= 0:
            return Response({"error": "Cantidad inválida"}, status=400)

        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=404)

        if cantidad > producto.stock:
            return Response({"error": "No hay suficiente stock"}, status=400)

        carrito = obtener_o_crear_carrito(request.user)

        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": producto.precio
            }
        )

        if not created:

            nueva_cantidad = item.cantidad + cantidad

            if nueva_cantidad > producto.stock:
                return Response({"error": "No hay suficiente stock"}, status=400)

            item.cantidad = nueva_cantidad
            item.save()

        serializer = CarritoSerializer(carrito)

        return Response(serializer.data, status=201)


# =========================================================
# ELIMINAR ITEM
# =========================================================

class EliminarProductoCarritoView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):

        try:
            item = CarritoItem.objects.get(id=item_id)
            item.delete()

            return Response({"mensaje": "Producto eliminado del carrito"})

        except CarritoItem.DoesNotExist:
            return Response({"error": "Item no encontrado"}, status=404)


# =========================================================
# VACIAR CARRITO
# =========================================================

class VaciarCarritoView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request):

        carrito = obtener_o_crear_carrito(request.user)

        carrito.items.all().delete()

        return Response({"mensaje": "Carrito vaciado correctamente"})


# =========================================================
# CONFIRMAR PEDIDO
# =========================================================

class ConfirmarPedidoView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        cliente = obtener_o_crear_cliente(request.user)

        try:
            carrito = Carrito.objects.get(cliente=cliente)
        except Carrito.DoesNotExist:
            return Response({"error": "No existe carrito activo"}, status=400)

        items_carrito = carrito.items.all()

        if not items_carrito.exists():
            return Response({"error": "El carrito está vacío"}, status=400)

        pedido = Pedido.objects.create(
            cliente=cliente,
            estado='pendiente'
        )

        total = 0

        for item in items_carrito:

            if item.cantidad > item.producto.stock:
                return Response(
                    {"error": f"No hay suficiente stock de {item.producto.nombre}"},
                    status=400
                )

            subtotal = item.cantidad * item.precio_unitario
            total += subtotal

            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )

            item.producto.stock -= item.cantidad
            item.producto.save()

        pedido.total = total
        pedido.estado = 'pagado'
        pedido.save()

        Pago.objects.create(
            pedido=pedido,
            metodo_pago='efectivo',
            monto=total,
            fecha_pago=timezone.now(),
            estado='aprobado'
        )

        carrito.items.all().delete()
        carrito.activo = False
        carrito.save()

        return Response({
            "mensaje": "Pedido confirmado y pagado",
            "pedido_id": pedido.id_pedido,
            "total": total
        }, status=201)


# =========================================================
# LISTAR PEDIDOS DEL CLIENTE (CON PAGINACIÓN)
# =========================================================

class ListarPedidosView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cliente = obtener_o_crear_cliente(request.user)

        pedidos = Pedido.objects.filter(
            cliente=cliente
        ).order_by('-fecha')

        paginator = PageNumberPagination()
        paginator.page_size = 5  # opcional (puede usar settings)

        result_page = paginator.paginate_queryset(pedidos, request)

        serializer = PedidoListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# =========================================================
# CANCELAR PEDIDO
# =========================================================

class CancelarPedidoView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pedido_id):

        cliente = obtener_o_crear_cliente(request.user)

        try:
            pedido = Pedido.objects.get(id_pedido=pedido_id, cliente=cliente)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=404)

        if pedido.estado == 'cancelado':
            return Response({"error": "El pedido ya está cancelado"}, status=400)

        for item in pedido.items.all():
            producto = item.producto
            producto.stock += item.cantidad
            producto.save()

        pedido.estado = 'cancelado'
        pedido.save()

        return Response({"mensaje": "Pedido cancelado correctamente"})


# =========================================================
# ADMIN - LISTAR PEDIDOS (CON PAGINACIÓN)
# =========================================================

class AdminListarPedidosView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        search = request.query_params.get("search", "").strip()

        pedidos = Pedido.objects.select_related(
            "cliente",
            "cliente__id_cliente"
        )

        if search:

            pedidos = pedidos.filter(
                Q(cliente__id_cliente__username__icontains=search) |
                Q(cliente__id_cliente__first_name__icontains=search) |
                Q(cliente__id_cliente__last_name__icontains=search)
            )

            if search.isdigit():
                pedidos = pedidos | Pedido.objects.filter(
                    id_pedido=int(search)
                )

        pedidos = pedidos.order_by("-fecha").distinct()

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(pedidos, request)

        from .serializers import PedidoAdminSerializer

        serializer = PedidoAdminSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

# =========================================================
# ADMIN - CAMBIAR ESTADO
# =========================================================

class AdminCambiarEstadoPedidoView(APIView):

    permission_classes = [IsAdminUser]

    def patch(self, request, pedido_id):

        try:
            pedido = Pedido.objects.get(id_pedido=pedido_id)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=404)

        nuevo_estado = request.data.get("estado")

        estados_validos = ['pendiente', 'pagado', 'enviado', 'entregado', 'cancelado']

        if nuevo_estado not in estados_validos:
            return Response({"error": "Estado inválido"}, status=400)

        pedido.estado = nuevo_estado
        pedido.save()

        return Response({
            "mensaje": "Estado actualizado correctamente",
            "pedido_id": pedido.id_pedido,
            "nuevo_estado": pedido.estado
        })

# =========================================================
# ADMIN - DETALLE PEDIDO
# =========================================================

class AdminDetallePedidoView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request, pedido_id):

        try:
            pedido = Pedido.objects.get(id_pedido=pedido_id)

        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=404)

        from .serializers import PedidoDetalleSerializer

        serializer = PedidoDetalleSerializer(pedido)

        return Response(serializer.data)


# =========================================================
# ADMIN - PEDIDOS POR ESTADO (🔥 NUEVO PARA DASHBOARD)
# =========================================================

from django.db.models import Count

class AdminPedidosPorEstadoView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            Pedido.objects
            .values('estado')
            .annotate(total=Count('*'))
            .order_by('estado')
        )

        return Response(data)