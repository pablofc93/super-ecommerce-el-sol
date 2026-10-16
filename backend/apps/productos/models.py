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
    categoria = models.ForeignKey( #ForeignKey significa que un producto puede pertenecer a una categoría, y una categoría puede tener muchos productos
        Categoria,
        on_delete=models.SET_NULL, #si una categoría se elimina, los productos de esa categoría no se eliminan
        null=True, #en lugar de eliminarse, las categorias eliminadas de esos productos serán null
        related_name="productos"
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    # 🆕 Imagen del producto
    imagen = models.ImageField( #ImageField es proporcionado por Django para manejar imágenes
        upload_to="productos/", #indica que los archivos cargados se almacenarán en la carpeta productos/
        null=True, #acepta que sea un campo nulo
        blank=True, #se acepta como campo vacío
        help_text="Imagen del producto"
    )

    creado_en = models.DateTimeField(auto_now_add=True) #auto_now_add = True establece automáticamente la fecha y hora de creación del objeto cuando se guarda por primera vez
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


# =========================
# Registro de compras - representa un registro de una compra realizada por un cliente
# =========================
class Compra(models.Model):

    #relación con cliente
    #un cliente puede tener muchas compras y cada compra pertenece a un cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="compras" #indica como acceder desde un cliente a sus compras //por ejemplo, se puede hacer: cliente.compras.all() trae todas las compras de un cliente
    )

    #relación con producto
    #un producto puede estar en muchas compras y cada compra pertenece a un producto
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="compras"
    )

    # PedidoItem del cual se originó la compra
    #un pedido item puede estar asociado a una compra
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