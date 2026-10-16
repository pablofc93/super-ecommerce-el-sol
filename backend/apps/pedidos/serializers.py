from rest_framework import serializers
from .models import Carrito, CarritoItem, Pedido, PedidoItem


# =========================
# ITEM DEL CARRITO
# =========================
class CarritoItemSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='producto.id', write_only=True) #se envía/recibe el campo producto_id
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True) #obtener el nombre desde el producto relacionado y mostrarlo como producto_nombre
    stock = serializers.IntegerField(source='producto.stock', read_only=True)

    #esta clase indica que el serializer trabaja con el modelo CarritoItem
    #fiels indica cuales son los campos que el serializer va a manejar
    class Meta:
        model = CarritoItem
        fields = [
            'id',
            'producto_id',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'stock'
        ]


# =========================
# CARRITO
# =========================
class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True) #many=True indica que el carrito puede contener múltiples elementos

    class Meta:
        model = Carrito
        fields = [
            'id',
            'cliente',
            'activo',
            'creado_en',
            'items'
        ]
        read_only_fields = [
            'cliente',
            'activo',
            'creado_en'
        ]


# =========================
# LISTAR PEDIDOS
# =========================
class PedidoListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pedido
        fields = [
            'id_pedido',
            'total',
            'estado',
            'fecha'
        ]


# =========================
# ADMIN LISTAR PEDIDOS
# =========================
class PedidoAdminSerializer(serializers.ModelSerializer):

    cliente_nombre = serializers.CharField(
        source='cliente.id_cliente.username',
        read_only=True
    )

    class Meta:
        model = Pedido
        fields = [
            'id_pedido',
            'cliente_nombre',
            'total',
            'estado',
            'fecha'
        ]


# =========================
# ADMIN DETALLE PEDIDO ITEM
# =========================
class PedidoDetalleItemSerializer(serializers.ModelSerializer):

    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )

    class Meta:
        model = PedidoItem
        fields = [
            'producto_nombre',
            'cantidad',
            'precio_unitario'
        ]


# =========================
# ADMIN DETALLE PEDIDO - está pensado para mostrar el detalle completo de un pedido desde el panel de administración
# =========================
class PedidoDetalleSerializer(serializers.ModelSerializer):

    cliente_nombre = serializers.CharField(
        source='cliente.id_cliente.username',
        read_only=True
    )

    items = PedidoDetalleItemSerializer(many=True, read_only=True) #items almacena cada uno de los elementos que componen el item del pedido

    class Meta:
        model = Pedido
        fields = [ #esto indica qué campos serán enviados al frontend
            'id_pedido',
            'cliente_nombre',
            'total',
            'estado',
            'fecha',
            'items'
        ]