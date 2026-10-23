
from rest_framework import serializers
from .models import Carrito, CarritoItem, Pedido, PedidoItem


# =========================
# ITEM DEL CARRITO
# =========================
class CarritoItemSerializer(serializers.ModelSerializer):
    # ID del producto enviado al agregar un artículo al carrito.
    producto_id = serializers.IntegerField(
        source='producto.id',
        write_only=True
    )

    # Datos del producto relacionado.
    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )

    stock = serializers.IntegerField(
        source='producto.stock',
        read_only=True
    )

    # URL de la imagen del producto.
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = CarritoItem
        fields = [
            'id',
            'producto_id',
            'producto_nombre',
            'imagen_url',
            'cantidad',
            'precio_unitario',
            'stock'
        ]

    def get_imagen_url(self, obj):
        """
        Devuelve la URL absoluta de la imagen del producto.
        Si el producto no tiene imagen, devuelve None.
        """
        producto = obj.producto

        if not producto.imagen:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(producto.imagen.url)

        return producto.imagen.url


# =========================
# CARRITO
# =========================
class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(
        many=True,
        read_only=True
    )

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

    items = PedidoDetalleItemSerializer(
        many=True,
        read_only=True
    )

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
