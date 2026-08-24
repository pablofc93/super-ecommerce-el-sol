#el serializer es el encargado de convertir los datos del modelo Usuario 
# a un formato que pueda ser enviado a través de la API, como JSON. 
# También se encarga de validar los datos que se reciben desde 
# la API antes de guardarlos en la base de datos.
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.clientes.models import Cliente

User = get_user_model()


# =========================
# REGISTRAR USUARIOS
# =========================
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    # 🔹 opcionales
    direccion = serializers.CharField(required=False, allow_blank=True)
    ciudad = serializers.CharField(required=False, allow_blank=True)
    provincia = serializers.CharField(required=False, allow_blank=True)
    codigo_postal = serializers.CharField(required=False, allow_blank=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    #esta clase Meta es una clase interna que se utiliza para definir 
    # metadatos sobre el serializer, como el modelo que se va a 
    # serializar y los campos que se van a incluir en la serialización.
    #en este caso, se indica que este serializer está relacionado con el modelo 
    # User que corresponde al modelo usuarios y que se van a incluir los campos id, username, 
    # email, password, first_name, last_name, 
    # tipo_usuario, direccion, ciudad, provincia y codigo_postal.
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'tipo_usuario',
            'direccion',
            'ciudad',
            'provincia',
            'codigo_postal'
        )
        read_only_fields = ('tipo_usuario',) #esta linea impide que el campo tipo_usuario sea modificado por el usuario, ya que siempre será 'cliente' al registrarse.

    def create(self, validated_data):

        #pop extae los datos validados de validated_data y los asigna a variables locales.
        #esto se hace debido a que estos datos se usan para la creacion de un usuario del tipo cliente.
        direccion = validated_data.pop('direccion', '')
        ciudad = validated_data.pop('ciudad', '')
        provincia = validated_data.pop('provincia', '')
        codigo_postal = validated_data.pop('codigo_postal', '')

        #crea el USUARIO y lo almacena en la base de datos.
        #se utiliza User.object.create_user para que la contraseña se guarde de forma segura en la bd.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            tipo_usuario='cliente'
        )

        # crear CLIENTE (no romper si falla)
        try:
            Cliente.objects.create(
                id_cliente=user,
                direccion=direccion,
                ciudad=ciudad,
                provincia=provincia,
                codigo_postal=codigo_postal
            )
        except Exception as e:
            print("ERROR CREANDO CLIENTE:", str(e))

        return user


# =========================
# USER (LOGIN / ME) aqui se indican que campos del usuario se pueden convertir en JSON, password no incluida
# =========================
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'tipo_usuario'
        )


# =========================
# CREACIÓN DE USUARIOS DEL TIPO ADMINISTRADOR
# =========================
class AdminUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    #este serializer trabaja con el modelo User y acepta/devuelve estos campos
    class Meta:
        model = User
        fields = ('id', 
                  'username', 
                  'email', 
                  'password', 
                  'tipo_usuario'
        )

    def create(self, validated_data):

        password = validated_data.pop('password', None)
        user = User(**validated_data)

        if password:
            user.set_password(password)

        user.save()
        return user


# =========================
# VALIDACIONES ANTES DE CAMBIAR LA CONTRASEÑA
# =========================
class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        #obtener el usuario autenticado que está realizando la solicitud de cambio de contraseña
        user = self.context['request'].user

        if not user.check_password(data['current_password']):
            raise serializers.ValidationError({
                "current_password": "La contraseña actual es incorrecta"
            })

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Las contraseñas no coinciden"
            })

        if len(data['new_password']) < 6:
            raise serializers.ValidationError({
                "new_password": "Debe tener al menos 6 caracteres"
            })

        return data