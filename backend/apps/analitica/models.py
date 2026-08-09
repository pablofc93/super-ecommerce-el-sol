from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# =====================================================
# PRODUCTO MÁS VENDIDO
# =====================================================
class ProductoMasVendido(models.Model):
    producto_id = models.IntegerField()
    nombre_producto = models.CharField(max_length=255)
    total_vendido = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto más vendido'
        verbose_name_plural = 'Productos más vendidos'
        constraints = [
            models.UniqueConstraint(
                fields=['producto_id', 'fecha_calculo'],
                name='unique_producto_por_dia'
            )
        ]

    def __str__(self):
        return f'{self.nombre_producto} ({self.total_vendido})'



# =====================================================
# CATEGORÍA MÁS MOVIDA
# =====================================================
class CategoriaMasMovida(models.Model):
    categoria_id = models.IntegerField()
    nombre_categoria = models.CharField(max_length=255)
    total_movimiento = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría más movida'
        verbose_name_plural = 'Categorías más movidas'
        unique_together = ('categoria_id', 'fecha_calculo')

    def clean(self):
        if self.total_movimiento <= 0:
            raise ValidationError("El total de movimiento debe ser mayor a cero.")

    def __str__(self):
        return f'{self.nombre_categoria} ({self.total_movimiento})'


# =====================================================
# INGRESOS POR CLIENTE
# =====================================================
""" class IngresoPorCliente(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ingreso por cliente'
        verbose_name_plural = 'Ingresos por cliente'
        unique_together = ('cliente', 'fecha_calculo')

    def clean(self):
        if self.total_ingresos <= 0:
            raise ValidationError("El ingreso total debe ser mayor a cero.")

    def __str__(self):
        return f'{self.cliente.username} - ${self.total_ingresos}' """


# =====================================================
# REGLAS DE ASOCIACIÓN
# =====================================================
class ReglaAsociacion(models.Model):
    productos = models.JSONField()  # ej: [1, 3, 7]
    soporte = models.FloatField()
    confianza = models.FloatField()
    lift = models.FloatField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Regla de asociación'
        verbose_name_plural = 'Reglas de asociación'

    def clean(self):
        if not self.productos or len(self.productos) < 2:
            raise ValidationError("Una regla debe contener al menos dos productos.")
        if not (0 < self.soporte <= 1):
            raise ValidationError("El soporte debe estar entre 0 y 1.")
        if not (0 < self.confianza <= 1):
            raise ValidationError("La confianza debe estar entre 0 y 1.")
        if self.lift <= 0:
            raise ValidationError("El lift debe ser mayor a cero.")


# =====================================================
# CLIENTE SEGMENTADO
# =====================================================
class ClienteSegmentado(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    cluster = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente segmentado'
        verbose_name_plural = 'Clientes segmentados'
        unique_together = ('cliente', 'fecha_calculo')
