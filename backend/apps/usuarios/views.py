#views.py contiene las vistas, es decir, el código que recibe las solicitudes del cliente y determina
#qué debe hacer el backend y que respuestas devolver

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import SessionAuthentication
from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer, ChangePasswordSerializer

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
    update_session_auth_hash
)
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer

#se obtiene el modelo de usuario que está configurado actualmente en Django y lo guarda en
#la variable User
User = get_user_model()


# Extiende SessionAuthentication para mantener la autenticación por sesión,
# pero desactiva la validación CSRF. Se utiliza en el logout para permitir
# que Angular cierre la sesión sin requerir el token CSRF.

# =========================
# PARA DESACTIVAR CSRF EN LOGOUT
# =========================
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# =========================
# PAGINACIÓN PERSONALIZADA
# =========================
class AdminUserPagination(PageNumberPagination):
    page_size = 5
    #esto es para que el frontend solicite la cantidad de usuarios 
    # por página que desea recibir, 
    # si no se especifica, se usará el valor por defecto de 5.
    page_size_query_param = 'page_size' 
    max_page_size = 50


# =========================
# CSRF VIEW
# =========================
@ensure_csrf_cookie
#recibe la solicitud HTTP y 
# devuelve una respuesta JSON que indica que la cookie CSRF se ha establecido correctamente.
def get_csrf(request): 
    return JsonResponse({'detail': 'CSRF cookie set'}) #


# =========================
# REGISTER
# =========================
class RegisterView(APIView):
    #AllowAny permite que el endpoint sea utilizado por usuarios que todavía no están autenticados, 
    # lo cual es necesario para el registro de nuevos usuarios.
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data) #instancia de la clase RegisterSerializer que está en serializers.py

        if serializer.is_valid():
            user = serializer.save() #los datos validados del ususario se guardan en user
            return Response(
                UserSerializer(user).data, #Instancia de la clase UserSerializer que recibe como parámetro el objeto user, este objeto ya tiene los datos validados del usuario
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# LOGIN
# =========================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username y password son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #authenticate permite que Django compruebe las credenciales proporcionadas
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        login(request, user)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )


# =========================
# LOGOUT
# =========================
class LogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(
            {'message': 'Sesión cerrada correctamente'},
            status=status.HTTP_200_OK
        )


# =========================
# ME - es para que el usuario autenticado consulte y modifique sus propios datos
# de perfil
# =========================
class MeView(APIView):
    #esto indica que esta vista es accedida solo por usuarios autenticados
    permission_classes = [IsAuthenticated]

    def get(self, request):
        #request.user representa al usuario asociado a la sesion autenticada
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tipo_usuario": user.tipo_usuario
        })

    #metodo para modificar el perfil del usuario
    #se utiliza PATCH porque no necesariamente se deben modificar todos los datos
    def patch(self, request):
        user = request.user

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if username:
            user.username = username

        if email:
            user.email = email

        if password:
            user.set_password(password) #almacena la contraseña pero cifrada
            user.save() #guarda la nueva contraseña

            #LOGOUT AUTOMÁTICO (CLAVE)
            logout(request)

            return Response({
                "message": "Contraseña actualizada. Debes iniciar sesión nuevamente."
            }, status=status.HTTP_200_OK)

        user.save()

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tipo_usuario": user.tipo_usuario
        }, status=status.HTTP_200_OK)


# =========================
# ADMIN - LISTAR USUARIOS
# =========================
class AdminListarUsuariosView(ListAPIView):
    permission_classes = [IsAdminUser] #esto significa que solo usuarios del tipo administrador puedan ejecutar esta vista
    serializer_class = AdminUserSerializer #se define el serializer que se va a usar para mostrar los datos de los usuarios. ('atributo' del tipo 'clase')
    queryset = User.objects.all().order_by('-date_joined') #obtener todos los registros del modelo Usuario y ordenarlos por fecha de creación de manera descendente

    pagination_class = AdminUserPagination
    filter_backends = [SearchFilter, OrderingFilter] #aqui se indica que esta vista tendrá la capacidad de filtrar y ordenar los resultados de la lista de usuarios
    search_fields = ['username', 'email'] #se indica que el admin podrá buscar por usuario o correo
    ordering_fields = ['id', 'username', 'date_joined'] #es posible ordenar por id, nombre de usuario o fecha de creación


# =========================
# ADMIN - CREAR USUARIOS
# =========================
class AdminCrearUsuarioView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                AdminUserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# ADMIN - CAMBIAR ROL
# =========================
class AdminCambiarRolView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id) #se busca el usuario en la base de datos mediante su id (user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        nuevo_rol = request.data.get("tipo_usuario") #se obtiene el valor del nuevo rol enviado desde el frontend

        #aqui se valida el nuevo rol para evitar que se carguen valores incorrectos
        if nuevo_rol not in ['cliente', 'admin']:
            return Response({"error": "Rol inválido"}, status=400)

        #modifica el rol del objeto user en memoria
        user.tipo_usuario = nuevo_rol
        #guardar el valor del nuevo rol del usuario en la base de datos
        user.save()

        return Response({
            "mensaje": "Rol actualizado correctamente",
            "id": user.id,
            "tipo_usuario": user.tipo_usuario
        })


# =========================
# ADMIN - ELIMINAR USUARIO
# =========================
class AdminEliminarUsuarioView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id): #el user_id se envia fuera de la request porque es parte de la url, no del cuerpo de la request (solicitud) que envía el front
        try:
            user = User.objects.get(id=user_id) #busca al usuario en la base de datos de acuerdo a su id
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        user.delete() #aqui es donde se elimina el usuario de la base de datos
        return Response({"mensaje": "Usuario eliminado correctamente"}) #devuelve una respuesta al frontend confirmando la eliminacion del usuario
    
# =========================
# CAMBIAR CONTRASEÑA
# =========================
class ChangePasswordView(APIView):
    #esto indica que solo los usuarios con una sesión válida pueden cambiar la contraseña
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer( #se crea una instancia del serializer ChangePasswordSerializer que se encuentra en serializers.py
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user #aqui se obtiene al usuario que realizó la solicitud
            user.set_password(serializer.validated_data['new_password']) #se establece la nueva contraseña
            user.save() #se guarda la nueva contraseña del usuario en la base de datos

            # luego de cambiar la contraseña se produce logout automático
            logout(request)

            return Response({
                "message": "Contraseña actualizada correctamente. Debes iniciar sesión nuevamente."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)