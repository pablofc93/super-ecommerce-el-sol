from rest_framework import serializers
from .models import Carrito, CarritoItem, Pedido, PedidoItem


# =========================
# ITEM DEL CARRITO
# =========================
class CarritoItemSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='producto.id', write_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    stock = serializers.IntegerField(source='producto.stock', read_only=True)

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
    items = CarritoItemSerializer(many=True, read_only=True)

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
# ADMIN DETALLE PEDIDO
# =========================
class PedidoDetalleSerializer(serializers.ModelSerializer):

    cliente_nombre = serializers.CharField(
        source='cliente.id_cliente.username',
        read_only=True
    )

    items = PedidoDetalleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id_pedido',
            'cliente_nombre',
            'total',
            'estado',
            'fecha',
            'items'
        ]