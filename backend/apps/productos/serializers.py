from rest_framework import serializers
from .models import Categoria, Producto, Compra


# =========================
# Categoría
# =========================
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


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
        required=False,
        allow_null=True,
        use_url=True  # ✅ clave para que devuelva la URL completa
    )

    # 🆕 Método para enviar URL absoluta (útil para frontend)
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        # incluir todos los campos + imagen_url
        fields = "__all__"
        # Si querés, también podés listar explícitamente:
        # fields = ['id', 'nombre', 'descripcion', 'precio', 'categoria', 'categoria_id', 'imagen', 'imagen_url']

    # Devuelve la URL completa absoluta de la imagen
    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen:
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
        queryset=Producto.objects.all(),
        source="producto",
        write_only=True
    )

    # Producto completo en lectura
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = Compra
        fields = [
            "id",
            "cliente",
            "producto",
            "producto_id",
            "cantidad",
            "fecha",
        ]
