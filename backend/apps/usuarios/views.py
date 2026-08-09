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


User = get_user_model()


# =========================
# 🔥 FIX CSRF PARA LOGOUT
# =========================
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# =========================
# PAGINACIÓN PERSONALIZADA
# =========================
class AdminUserPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


# =========================
# CSRF VIEW
# =========================
@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({'detail': 'CSRF cookie set'})


# =========================
# REGISTER
# =========================
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
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
# 🔥 LOGOUT (FIX DEFINITIVO)
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
# ME
# =========================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tipo_usuario": user.tipo_usuario
        })

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
            user.set_password(password)
            user.save()

            # 🔥 LOGOUT AUTOMÁTICO (CLAVE)
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
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by('-date_joined')

    pagination_class = AdminUserPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['id', 'username', 'date_joined']


# =========================
# ADMIN - CREAR USUARIO
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
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        nuevo_rol = request.data.get("tipo_usuario")

        if nuevo_rol not in ['cliente', 'admin']:
            return Response({"error": "Rol inválido"}, status=400)

        user.tipo_usuario = nuevo_rol
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

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        user.delete()
        return Response({"mensaje": "Usuario eliminado correctamente"})
    
# =========================
# CHANGE PASSWORD
# =========================
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # 🔥 logout automático
            logout(request)

            return Response({
                "message": "Contraseña actualizada correctamente. Debes iniciar sesión nuevamente."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)