from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.recomendacion.services.personalizadas import (
    RecomendacionPersonalizadaService
)
from apps.productos.serializers import ProductoSerializer
from apps.clientes.models import Cliente


class RecomendacionPorClienteView(APIView):
    """
    Devuelve recomendaciones personalizadas para un cliente
    en base a su historial de pedidos.
    """
    permission_classes = [AllowAny]

    def get(self, request, id_cliente):
        # 1️⃣ Verificar que el cliente exista
        if not Cliente.objects.filter(id_cliente=id_cliente).exists():
            return Response(
                {"detail": "Cliente no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2️⃣ Obtener recomendaciones
        productos = RecomendacionPersonalizadaService.recomendar_productos_por_cliente(
            cliente_id=id_cliente
        )

        # 3️⃣ Serializar respuesta
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecomendacionPorCategoriaFavoritaView(APIView):
    """
    Devuelve productos según la categoría más comprada por el cliente.
    Si no hay datos suficientes, aplica fallback a productos más vendidos.
    """
    permission_classes = [AllowAny]

    def get(self, request, id_cliente):
        # 1️⃣ Verificar que el cliente exista
        if not Cliente.objects.filter(id_cliente=id_cliente).exists():
            return Response(
                {"detail": "Cliente no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2️⃣ Obtener recomendaciones
        productos = RecomendacionPersonalizadaService.recomendar_por_categoria_favorita(
            cliente_id=id_cliente
        )

        # 3️⃣ Serializar respuesta
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
