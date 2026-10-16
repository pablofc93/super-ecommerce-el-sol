# Este signal sirve para que cada vez que se cree una compra, se reste
# automáticamente del stock del producto.

from django.db.models.signals import post_save, pre_save, post_delete #señales que se ejecutan de forma automática
from django.dispatch import receiver
from .models import Compra, Producto


# =========================================
# RESTAR STOCK CUANDO SE CREA UNA COMPRA - post_save
# =========================================
@receiver(post_save, sender=Compra)
def actualizar_stock(sender, instance, created, **kwargs):
    """
    Cada vez que se crea una Compra, se resta la cantidad del stock del Producto.
    """
    if created: #si created es True, se obtiene el producto relacionado
        producto = instance.producto
        if producto.stock >= instance.cantidad:
            producto.stock -= instance.cantidad
            producto.save()
        else:
            # Opcional: lanzar una advertencia si no hay stock suficiente
            print(f"Advertencia: Stock insuficiente para el producto {producto.nombre}")


# =========================================
# ELIMINAR IMAGEN AL BORRAR PRODUCTO - post_delete
# =========================================
@receiver(post_delete, sender=Producto) #sender=Producto significa: esta señal está asociada al modelo Producto
def eliminar_imagen_producto(sender, instance, **kwargs):
    """
    Elimina la imagen del sistema de archivos cuando se elimina un producto.
    """
    if instance.imagen:
        instance.imagen.delete(save=False) #save=False indica que no es necesario volver a guardar el objeto Producto, ya que fue eliminado de la bd


# =========================================
# ELIMINAR IMAGEN VIEJA AL REEMPLAZARLA - pre_save
# =========================================
@receiver(pre_save, sender=Producto)
def eliminar_imagen_anterior(sender, instance, **kwargs):
    """
    Cuando se actualiza un producto y se cambia la imagen,
    elimina la imagen anterior del disco.
    """

    # Si el producto aún no existe (creación), no hacemos nada
    if not instance.pk:
        return

    try:
        producto_anterior = Producto.objects.get(pk=instance.pk)
    except Producto.DoesNotExist:
        return

    imagen_anterior = producto_anterior.imagen
    nueva_imagen = instance.imagen

    # Si existe imagen anterior y es diferente a la nueva
    if imagen_anterior and imagen_anterior != nueva_imagen:
        imagen_anterior.delete(save=False)