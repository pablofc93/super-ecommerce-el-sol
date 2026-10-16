from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# =====================================================
# PRODUCTO MÁS VENDIDO
# =====================================================
class ProductoMasVendido(models.Model):
    producto_id = models.IntegerField() #no es un ForeignKey porque el producto puede ser eliminado y queremos mantener el registro histórico
    nombre_producto = models.CharField(max_length=255)
    total_vendido = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto más vendido' #indica el nombre del modelo en singular en el admin
        verbose_name_plural = 'Productos más vendidos' #indica el nombre del modelo en plural en el admin
        constraints = [
            models.UniqueConstraint(
                fields=['producto_id', 'fecha_calculo'], #indica que la combinación de producto_id y fecha_calculo debe ser única
                name='unique_producto_por_dia' #nombre de la restricción
            )
        ]

    def __str__(self):
        return f'{self.nombre_producto} ({self.total_vendido})'



# =====================================================
# CATEGORÍA MÁS MOVIDA - almacena el resultado de las categorías que tuvieron más movimiento en ventas, 
# para cada día. Esto permite analizar tendencias y patrones de compra por categoría.
# =====================================================
class CategoriaMasMovida(models.Model):
    categoria_id = models.IntegerField() # almacena el identificador de la categoría
    nombre_categoria = models.CharField(max_length=255)
    total_movimiento = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    # esta clase permite configurar diferentes características del modelo
    class Meta:
        verbose_name = 'Categoría más movida' # nombre del modelo en singular en el admin
        verbose_name_plural = 'Categorías más movidas' # nombre del modelo en plural en el admin
        unique_together = ('categoria_id', 'fecha_calculo') # asegura que no haya duplicados de categoría por fecha

    # regla personalizada de validación para asegurar que el total de movimiento sea mayor a cero
    def clean(self):
        if self.total_movimiento <= 0:
            raise ValidationError("El total de movimiento debe ser mayor a cero.")

    # método que define cómo se representa el objeto como cadena, útil para mostrar en el admin o en logs
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
# Clase que define el modelo que sirve para guardar las relaciones encontradas entre productos
# mediante un análisis de reglas de asociación
class ReglaAsociacion(models.Model):
    productos = models.JSONField()  # ej: [1, 3, 7]
    soporte = models.FloatField() # indica que tan frecuente aparece una comb de prod dentro de un conjunto de transacciones
    confianza = models.FloatField() # cuando alguien compra A, que tan probable es que compre B
    lift = models.FloatField() # indica que tan fuerte es esa asociación de productos
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
# CLIENTE SEGMENTADO - define como almacenar los los datos 
# los registros sobre a qué grupo o cluster pertenece cada cliente, 
# según el análisis de segmentación realizado.
# =====================================================
class ClienteSegmentado(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE) #establece la relación con el modelo de usuario, indicando que cada registro pertenece a un cliente específico
    cluster = models.PositiveIntegerField()
    fecha_calculo = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente segmentado'
        verbose_name_plural = 'Clientes segmentados'
        unique_together = ('cliente', 'fecha_calculo') # no puede existir más de un registro para el mismo cliente en la misma fecha
