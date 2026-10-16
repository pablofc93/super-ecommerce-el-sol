# apps/pedidos/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count
from .models import Carrito, CarritoItem, Pedido, PedidoItem, Pago
from .serializers import CarritoSerializer, PedidoListSerializer
from apps.clientes.models import Cliente
from apps.productos.models import Producto

# Funciones auxiliares
# =========================================================
# Este método busca un cliente asociado al usuario que se recibe como parámetro, y si no lo encutra, lo crea
# =========================================================
def obtener_o_crear_cliente(usuario): #usuario representa un objeto del modelo Usuario
    cliente, created = Cliente.objects.get_or_create( #get_or_create es un método de Django
        id_cliente=usuario #se busca un id_cliente que sea el mismo que el id de un usuario
    )
    return cliente

# =========================================================
# Este método obtiene el carrito correspondiente a un usuario,
# y si el carrito está como inactivo, lo activa,
# y si no existe, lo crea
# =========================================================
def obtener_o_crear_carrito(usuario):
    cliente = obtener_o_crear_cliente(usuario)
    carrito, created = Carrito.objects.get_or_create( #buscar un objeto (carrito) que cumpla determinada condición, y si no existe, crearlo
        cliente=cliente #(campo cliente del modelo Carrito) = (objeto cliente que se tiene en la variable)
        #buscar un Carrito cuyo campo cliente sea igual al objeto cliente
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
        carrito = obtener_o_crear_carrito(request.user) #este método recibe como parámetro el usuario autenticado
        serializer = CarritoSerializer(carrito) #se utiliza CarritoSerializer para convertir el objeto en JSON
        return Response(serializer.data) #se devuelve al frontend la información serializada del carrito

# =========================================================
# AGREGAR PRODUCTO AL CARRITO
# =========================================================
#hereda de APIView, lo que permite crear los métodos HTTP (get, post, put/patch, delete) para manejar las solicitudes del cliente
class AgregarProductoCarritoView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        producto_id = request.data.get("producto_id") #se obtiene el id del producto que se quiere agregar al carrito desde la solicitud del cliente
        cantidad = request.data.get("cantidad", 1) #se obtiene la cantidad de productos que se quieren agregar al carrito desde la solicitud del cliente, si no se especifica, se asume 1
        if not producto_id: #verificar que exista el producto_id, si no existe, se devuelve un error 400 (Bad Request) con un mensaje de error
            return Response({"error": "Falta producto_id"}, status=400)
        try:
            cantidad = int(cantidad)
        except ValueError:
            return Response({"error": "Cantidad inválida"}, status=400) #si se envia cantidad: "abc", da error
        if cantidad <= 0: #verificar que la cantidad sea mayor que 0
            return Response({"error": "Cantidad inválida"}, status=400)
        try:
            #equivalente a: SELECT * FROM productos_producto WHERE id = producto_id
            producto = Producto.objects.get(id=producto_id) #busca en la bd el producto con el id que se recibió en la solicitud del cliente y lo asigna a la variable producto
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=404)
        if cantidad > producto.stock:
            return Response({"error": "No hay suficiente stock"}, status=400)
        #llamada a una función, y su resultado se asigna a la variable carrito.
        # Esta función busca un carrito activo para el usuario autenticado, y si no lo encuentra, lo crea.
        carrito = obtener_o_crear_carrito(request.user)
        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": producto.precio
            }
        )
        #si el producto ya estaba en el carrito, se actualiza la cantidad sumando la nueva cantidad a la existente.
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
        carrito.items.all().delete() #obtiene todos los elementos del carrito y los elimina
        return Response({"mensaje": "Carrito vaciado correctamente"})

# =========================================================
# CONFIRMAR PEDIDO
# =========================================================
class ConfirmarPedidoView(APIView):
    permission_classes = [IsAuthenticated]
    #el decorador @transaction.atomic asegura que todas las operaciones dentro del método post se ejecuten como una única transacción.
    # Si alguna de las operaciones falla, todas las demás se revertirán, garantizando la integridad de los datos.
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
        #para cada item en el carrito, se verifica si hay suficiente stock del producto. Si no hay suficiente stock, se devuelve un error.
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
        #registro del pago en la tabla de pagos, con el estado 'aprobado' y el método de pago 'efectivo'
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
        ##se filtran los pedidos del cliente autenticado y se ordenan por fecha descendente (los más recientes primero)
        pedidos = Pedido.objects.filter(
            cliente=cliente
        ).order_by('-fecha')
        paginator = PageNumberPagination() #se crea una nueva instancia de PageNumberPagination, que es una clase proporcionada por Django REST Framework para manejar la paginación de resultados.
        paginator.page_size = 5  # opcional (puede usar settings) - cada página tendrá como máximo 5 pedidos
        #paginate_queryset es un método que toma un queryset
        # (en este caso, los pedidos del cliente) y la solicitud HTTP,
        # y devuelve una página con los primero 5 pedidos (o menos si no hay suficientes).
        result_page = paginator.paginate_queryset(pedidos, request) #contiene los pedidos de la página actual, según la paginación configurada.
        serializer = PedidoListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# =========================================================
# CANCELAR PEDIDO
# =========================================================
class CancelarPedidoView(APIView):
    permission_classes = [IsAuthenticated]
    #transaction.atomic asegura que todas las operaciones dentro del método post se ejecuten como una única transacción.
    #si todas las operaciones se completan correctamente, los cambios se confirman en la base de datos.
    #si alguna de las operaciones falla, todas las demás se revertirán, garantizando la integridad de los datos.
    @transaction.atomic
    def post(self, request, pedido_id):
        cliente = obtener_o_crear_cliente(request.user)
        try:
            pedido = Pedido.objects.get(id_pedido=pedido_id, cliente=cliente)
        except Pedido.DoesNotExist:
            return Response({"error": "Pedido no encontrado"}, status=404)
        if pedido.estado == 'cancelado':
            return Response({"error": "El pedido ya está cancelado"}, status=400)
        #se recorren los elementos del pedido y
        # se devuelve el stock de cada producto al inventario,
        # sumando la cantidad del item al stock actual del producto.
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
        #querey_params permite acceder a los parámetros de consulta de la URL, como ?search=valor.
        #.get() permite obtener el valor de un parámetro específico, en este caso "search".
        # si no lo encuentra, devuelve una cadena vacía. .strip() elimina espacios en blanco al inicio y al final del valor obtenido.
        search = request.query_params.get("search", "").strip()
        pedidos = Pedido.objects.select_related(
            "cliente", #seleccionar el cliente relacionado con el pedido
            "cliente__id_cliente" #esto permite acceder a pedidos->cliente->id_cliente, que es el usuario relacionado con el cliente
        )
        if search: #si search contiene un valor, se ejecuta el codigo dentro del if
            pedidos = pedidos.filter(
                #la Q significa que se pueden combinar múltiples condiciones de búsqueda usando operadores lógicos (AND, OR).
                #busca pedidos por nombre de usuario o nombre o apellido
                Q(cliente__id_cliente__username__icontains=search) |
                Q(cliente__id_cliente__first_name__icontains=search) |
                Q(cliente__id_cliente__last_name__icontains=search)
            )
            #esta comprobación es para buscarpor el id del pedido si el valor de búsqueda es un número.
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
    permission_classes = [IsAdminUser] #indica que solamente un usuario administrador puede acceder a esta vista
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
# ADMIN - CANTIDAD DE PEDIDOS AGRUPADOS POR ESTADO (DASHBOARD)
# =========================================================
class AdminPedidosPorEstadoView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        data = (
            Pedido.objects
            .values('estado')
            .annotate(total=Count('*')) #se cuenta cuantos valores hay en cada grupo
            .order_by('estado')
        )
        return Response(data)