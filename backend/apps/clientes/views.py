# apps/clientes/views.py
#este archivo se encarga de recibir las solicitudes HTTP y devolver respuestas HTTP para la app de clientes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse

from .models import Cliente
from .serializers import ClienteSerializer

#este método sirve para comprobar que la API esté funcionando correctamente
def home_cliente(request):
    return JsonResponse({"message": "Clientes API funcionando"})

#esta vista representa el perfil del cliente autenticado
class ClienteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # -------------------------------
    # OBTENER PERFIL DEL CLIENTE
    # -------------------------------
    def get(self, request):

        # 🔥 Garantiza que el usuario tenga un Cliente asociado
        #cliente: modelo de django que se está utilizando, son los datos del cliente
        #.objects: encargado de realizar consultas a la base de datos
        #get_or_create: busca un objeto que cumpla con los criterios especificados, si no lo encuentra, crea uno nuevo
        #id_cliente=request.user: criterio de búsqueda, busca un cliente cuyo id_cliente sea igual al usuario autenticado
        #request.user: representa al usuario autenticado que realiza la solicitud
        cliente, created = Cliente.objects.get_or_create(
            id_cliente=request.user
        )

        #aqui se toma el objeto cliente y se lo transorma con ClienteSerializer para poder devolverlo como JSON
        serializer = ClienteSerializer(cliente) 

        return Response(serializer.data) #devuelve el perfil con los datos serializados (en JSON)

    # -------------------------------
    # ACTUALIZAR PERFIL DEL CLIENTE
    # -------------------------------
    def patch(self, request):

        # Garantiza que el usuario tenga un Cliente asociado
        cliente, created = Cliente.objects.get_or_create(
            id_cliente=request.user
        )

        serializer = ClienteSerializer(
            cliente,
            data=request.data,
            partial=True #significa que se va a hacer una actualización parcial de los datos del cliente
        )

        serializer.is_valid(raise_exception=True) #se validan los datos recibidos
        serializer.save() #se guardan los datos modificados

        return Response(serializer.data) #se devuelve una respuesta


# -------------------------------
# CARRITO - vista destinada a manejar el carrito de compras 
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