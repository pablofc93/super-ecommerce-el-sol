from rest_framework import serializers
from .models import ReporteHistorico


# =========================
# Serializer de modelo
# =========================
class ReporteHistoricoSerializer(serializers.ModelSerializer):
    generado_por = serializers.StringRelatedField()

    class Meta:
        model = ReporteHistorico
        fields = (
            'id',
            'tipo',
            'fecha_generacion',
            'data',
            'generado_por',
        )


# =========================
# Serializers de reporting
# =========================
class ProductoMasVendidoSerializer(serializers.Serializer):
    producto = serializers.CharField()
    cantidad = serializers.IntegerField()


class CategoriaMasMovidaSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    total_ventas = serializers.IntegerField()


class SegmentacionClientesSerializer(serializers.Serializer):
    cluster = serializers.IntegerField()
    cantidad_clientes = serializers.IntegerField()


class DashboardSerializer(serializers.Serializer):
    ventas_totales = serializers.DecimalField(max_digits=12, decimal_places=2)
    producto_mas_vendido = ProductoMasVendidoSerializer()
    categoria_mas_movida = serializers.CharField()
    clientes_segmentados = SegmentacionClientesSerializer(many=True)


# =========================
# NUEVO: Ingresos por cliente
# =========================
class IngresosPorClienteSerializer(serializers.Serializer):
    cliente = serializers.IntegerField()
    cliente_nombre = serializers.CharField()
    cliente_email = serializers.EmailField()  # 🔥 mejor tipo
    total_ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)