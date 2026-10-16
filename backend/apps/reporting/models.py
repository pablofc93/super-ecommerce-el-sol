#Reporting NO recalcula, pero si puede guardar snapshots históricos.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReporteHistorico(models.Model):
    TIPO_REPORTE_CHOICES = (
        # valor que se guarda en la base de datos, nombre que se le muestra al usuario
        ('dashboard', 'Dashboard General'),
        ('ventas', 'Reporte de Ventas'),
        ('analitica', 'Reporte Analítico'),
        ('recomendacion', 'Reporte de Recomendación'),
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_REPORTE_CHOICES
    )

    fecha_generacion = models.DateTimeField(auto_now_add=True)

    # este campo permite almacenar información en formato JSON
    data = models.JSONField(
        help_text="Snapshot del reporte generado"
    )

    # campo relacionado con el modelo Usuario
    # un usuario puede generar muchos reportes
    generado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, # indica que admite valores nulos
        blank=True, # indica que puede ser un campo vacío
        related_name='reportes_generados'
    )

    class Meta:
        verbose_name = 'Reporte Histórico'
        verbose_name_plural = 'Reportes Históricos'
        ordering = ['-fecha_generacion']

    # este método especial define como se representa el objeto como texto
    # ej, devuelve: Reporte de Ventas - 2026-09-23 12:43
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"
