#Reporting NO recalcula, pero si puede guardar snapshots históricos.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReporteHistorico(models.Model):
    TIPO_REPORTE_CHOICES = (
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

    data = models.JSONField(
        help_text="Snapshot del reporte generado"
    )

    generado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_generados'
    )

    class Meta:
        verbose_name = 'Reporte Histórico'
        verbose_name_plural = 'Reportes Históricos'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_generacion.strftime('%Y-%m-%d %H:%M')}"
