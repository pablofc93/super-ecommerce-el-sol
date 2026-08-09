from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):

    # 🔹 datos del usuario
    username = serializers.CharField(source='id_cliente.username')
    email = serializers.EmailField(source='id_cliente.email')

    first_name = serializers.CharField(
        source='id_cliente.first_name',
        allow_blank=True,
        required=False
    )

    last_name = serializers.CharField(
        source='id_cliente.last_name',
        allow_blank=True,
        required=False
    )

    # 🔥 CORREGIDO → ahora pertenece a Cliente
    telefono = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Cliente
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'telefono',
            'direccion',
            'ciudad',
            'provincia',
            'codigo_postal',
        ]

    def update(self, instance, validated_data):

        user_data = validated_data.pop('id_cliente', {})

        user = instance.id_cliente

        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)

        if 'password' in user_data:
            user.set_password(user_data['password'])

        user.save()

        # 🔥 cliente
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.direccion = validated_data.get('direccion', instance.direccion)
        instance.ciudad = validated_data.get('ciudad', instance.ciudad)
        instance.provincia = validated_data.get('provincia', instance.provincia)
        instance.codigo_postal = validated_data.get('codigo_postal', instance.codigo_postal)

        instance.save()

        return instance