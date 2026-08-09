from django.db import models
from apps.clientes.models import Cliente
from apps.productos.models import Producto
from django.utils import timezone


# =========================
# CARRITO
# =========================

class Carrito(models.Model):
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Carrito de {self.cliente.id_cliente.username}"


class CarritoItem(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='carrito_items'
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["carrito", "producto"],
                name="unique_producto_por_carrito",
            )
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# =========================
# PEDIDO
# =========================

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    id_pedido = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha = models.DateTimeField(
        default=timezone.now
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente.id_cliente.username}"


class PedidoItem(models.Model):
    id_pedido_item = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='pedido_items'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# =========================
# PAGO
# =========================

class Pago(models.Model):
    METODO_CHOICES = (
        ('tarjeta', 'Tarjeta'),
        ('debito', 'Debito'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    )

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='pago'
    )
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    def __str__(self):
        return f"Pago Pedido #{self.pedido.id_pedido}"   