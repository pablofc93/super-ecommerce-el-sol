#repasar este serializer
from rest_framework import serializers #se importa el módulo de Django REST Framework que permite crear serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):

    # 🔹 datos del usuario
    username = serializers.CharField(source='id_cliente.username') #para llenar el campo username del JSON, buscar el valor del id_cliente que se relaciona con el usuario
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

    telefono = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False
    )

    #esta clase define qué campos van a aparecer en el JSON
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

    #este método se ejecuta cuando se necesita actualizar un cliente existente
    #instance es el cliente que ya existe en la bd
    #validated_data son los datos recibidos y validados
    def update(self, instance, validated_data):
        user_data = validated_data.pop('id_cliente', {}) #se obtiene la información asociada al Usuario
        user = instance.id_cliente #se obtiene el usuario

        #se actualizan los datos
        user.username = user_data.get('username', user.username) #si se recibe un nuevo username se actualiza, sino se mantiene el mismo
        user.email = user_data.get('email', user.email)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)

        #si se recibe una nueva contraseña se la hashea y se la actualiza, sino no hace nada
        if 'password' in user_data:
            user.set_password(user_data['password'])

        user.save() #guarda los datos del usuario

        # 🔥 cliente
        instance.telefono = validated_data.get('telefono', instance.telefono) #si llega un nuevo teléfono se actualiza, sino se mantiene el mismo
        instance.direccion = validated_data.get('direccion', instance.direccion)
        instance.ciudad = validated_data.get('ciudad', instance.ciudad)
        instance.provincia = validated_data.get('provincia', instance.provincia)
        instance.codigo_postal = validated_data.get('codigo_postal', instance.codigo_postal)

        instance.save() #guarda los datos del cliente asociado al usuario

        return instance #devuelve el objeto cliente actualizado