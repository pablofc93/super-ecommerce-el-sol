from django.db import models
from apps.clientes.models import Cliente


# =========================
# Categoría de productos
# =========================
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# =========================
# Producto
# =========================
class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name="productos"
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    # 🆕 Imagen del producto
    imagen = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        help_text="Imagen del producto"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


# =========================
# Registro de compras
# =========================
class Compra(models.Model):

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="compras"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="compras"
    )

    # PedidoItem del cual se originó la compra
    pedido_item = models.OneToOneField(
        "pedidos.PedidoItem",
        on_delete=models.CASCADE,
        related_name="compra",
        null=True,
        blank=True
    )

    cantidad = models.PositiveIntegerField(default=1)

    # Fecha histórica de la compra
    fecha = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.cliente.id_cliente.username} "
            f"compró {self.cantidad} x "
            f"{self.producto.nombre}"
        )