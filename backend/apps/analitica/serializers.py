from rest_framework import serializers
from .models import (
    ProductoMasVendido,
    CategoriaMasMovida,
    ReglaAsociacion,
    ClienteSegmentado
)


# =====================================================
# PRODUCTOS MÁS VENDIDOS
# =====================================================
class ProductoMasVendidoSerializer(serializers.ModelSerializer):

    def validate_total_vendido(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El total vendido debe ser mayor a cero."
            )
        return value

    class Meta:
        model = ProductoMasVendido
        fields = '__all__'


# =====================================================
# CATEGORÍAS MÁS MOVIDAS
# =====================================================
class CategoriaMasMovidaSerializer(serializers.ModelSerializer):

    def validate_total_movimiento(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El total de movimiento debe ser mayor a cero."
            )
        return value

    class Meta:
        model = CategoriaMasMovida
        fields = '__all__'


# =====================================================
# CLIENTES SEGMENTADOS
# =====================================================
class ClienteSegmentadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClienteSegmentado
        fields = '__all__'


# =====================================================
# REGLAS DE ASOCIACIÓN (APRIORI)
# =====================================================
class ReglaAsociacionSerializer(serializers.ModelSerializer):

    def validate_soporte(self, value):
        if value <= 0 or value > 1:
            raise serializers.ValidationError(
                "El soporte debe estar entre 0 y 1."
            )
        return value

    def validate_confianza(self, value):
        if value <= 0 or value > 1:
            raise serializers.ValidationError(
                "La confianza debe estar entre 0 y 1."
            )
        return value

    def validate_lift(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El lift debe ser mayor a cero."
            )
        return value

    class Meta:
        model = ReglaAsociacion
        fields = '__all__'