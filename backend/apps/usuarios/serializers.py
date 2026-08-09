from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.clientes.models import Cliente

User = get_user_model()


# =========================
# REGISTER
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
        read_only_fields = ('tipo_usuario',)

    def create(self, validated_data):

        direccion = validated_data.pop('direccion', '')
        ciudad = validated_data.pop('ciudad', '')
        provincia = validated_data.pop('provincia', '')
        codigo_postal = validated_data.pop('codigo_postal', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            tipo_usuario='cliente'
        )

        # 🔥 crear cliente (no romper si falla)
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
# USER (LOGIN / ME)
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
# ADMIN USER
# =========================
class AdminUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'tipo_usuario')

    def create(self, validated_data):

        password = validated_data.pop('password', None)
        user = User(**validated_data)

        if password:
            user.set_password(password)

        user.save()
        return user


# =========================
# CHANGE PASSWORD
# =========================
class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
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