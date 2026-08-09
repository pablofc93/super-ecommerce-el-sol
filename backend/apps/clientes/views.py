# apps/clientes/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse

from .models import Cliente
from .serializers import ClienteSerializer


def home_cliente(request):
    return JsonResponse({"message": "Clientes API funcionando"})


class ClienteProfileView(APIView):

    permission_classes = [IsAuthenticated]

    # -------------------------------
    # OBTENER PERFIL DEL CLIENTE
    # -------------------------------

    def get(self, request):

        # 🔥 Garantiza que el usuario tenga un Cliente asociado
        cliente, created = Cliente.objects.get_or_create(
            id_cliente=request.user
        )

        serializer = ClienteSerializer(cliente)

        return Response(serializer.data)

    # -------------------------------
    # ACTUALIZAR PERFIL DEL CLIENTE
    # -------------------------------

    def patch(self, request):

        # 🔥 Garantiza que el usuario tenga un Cliente asociado
        cliente, created = Cliente.objects.get_or_create(
            id_cliente=request.user
        )

        serializer = ClienteSerializer(
            cliente,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# -------------------------------
# CARRITO
# -------------------------------

class CarritoView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "Endpoint del carrito (pendiente de implementación)"
        })


# -------------------------------
# CHECKOUT
# -------------------------------

class CheckoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        return Response({
            "message": "Checkout pendiente de implementación"
        })


# -------------------------------
# HISTORIAL DE PEDIDOS
# -------------------------------

class HistorialPedidosView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "Historial de pedidos pendiente de implementación"
        })


# -------------------------------
# DETALLE PEDIDO
# -------------------------------

class DetallePedidoView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id):

        return Response({
            "pedido_id": pedido_id,
            "message": "Detalle de pedido pendiente de implementación"
        })