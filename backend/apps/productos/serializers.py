from rest_framework import serializers
from .models import Categoria, Producto, Compra


# =========================
# Categoría
# =========================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__" #indica que se incluyen todos los campos definidos en Categoria


# =========================
# Producto
# =========================
class ProductoSerializer(serializers.ModelSerializer):
    # Para enviar el ID de la categoría al crear/editar
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source="categoria",
        write_only=True,
        required=False,
        allow_null=True
    )

    # Para leer la categoría completa
    categoria = CategoriaSerializer(read_only=True)

    # 🆕 Campo de imagen
    # use_url=True asegura que se devuelva la URL completa usando MEDIA_URL
    imagen = serializers.ImageField(
        required=False, #indica que la imagen no es obligatoria
        allow_null=True, #permite que el valor sea "imagen": null
        use_url=True  #hace que DRF represente el archivo mediante su URL
    )

    # 🆕 Método para enviar URL absoluta (útil para frontend)
    imagen_url = serializers.SerializerMethodField()

    class Meta: # esta serializer trabaja con el modelo producto
        model = Producto
        fields = "__all__" # y se necesitan incluir todos los campos
        # Si querés, también podés listar explícitamente:
        # fields = ['id', 'nombre', 'descripcion', 'precio', 'categoria', 'categoria_id', 'imagen', 'imagen_url']

    # Devuelve la URL completa absoluta de la imagen
    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen: #¿este producto tiene una imagen?
            # request.build_absolute_uri asegura que devuelva URL completa http://127.0.0.1:8000/media/...
            return request.build_absolute_uri(obj.imagen.url)
        return None


# =========================
# Compra
# =========================
class CompraSerializer(serializers.ModelSerializer):
    # Cliente siempre en lectura
    cliente = serializers.PrimaryKeyRelatedField(read_only=True)

    # Para enviar el ID del producto al crear/editar
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), #el id del producto enviado desde el front debe buscarse en la bd para determinar si existe
        source="producto",
        write_only=True #indica que este campo solo se utiliza cuando se envian datos desde el front al back
    )

    # Producto completo en lectura - para leer se devuelve el producto completo
    producto = ProductoSerializer(read_only=True)
    # la clase meta establece qué modelo y qué campos serán manejados por el serializer
    class Meta:
        model = Compra #indica que el serializer está asociado al modelo compra
        fields = [
            "id",
            "cliente",
            "producto",
            "producto_id",
            "cantidad",
            "fecha",
        ]
