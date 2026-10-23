from django.db.models import Case, Count, IntegerField, Max, Sum, When
from apps.pedidos.models import PedidoItem
from apps.productos.models import Producto
from apps.analitica.models import ProductoMasVendido


class RecomendacionPersonalizadaService:
    """
    Servicio de recomendaciones personalizadas basado en:
    - historial de compras del cliente
    - categorías favoritas
    - fallback a productos más vendidos, calculado desde analítica o pedidos
    """
    # es un método estático, es decir, no necesita trabajar desde la instancia de esta clase, sino dentro de
    # la propia clase
    # * indica que los parámetros que aparecen después deben proporcionarse utilizando argumentos nombrados
    @staticmethod # indica que es un método estático
    def recomendar_productos_por_cliente(*, cliente_id, limite=5):
        """
        Recomienda productos según el historial de compras del cliente.
        Prioriza productos de categorías frecuentes y excluye los ya comprados.
        """

        # ---------------------------------------------
        # 1️⃣ Consulta de productos comprados por el cliente
        # ---------------------------------------------
        # productos_comprados contiene los id de los productos que el cliente compró en pedidos
        # considerados válidos
        productos_comprados = PedidoItem.objects.filter(
            pedido__cliente__id_cliente=cliente_id,
            pedido__estado__in=['pagado', 'enviado', 'entregado']
        ).values_list('producto_id', flat=True) # se obtiene solamente los id de los productos y flat true hace que se devuelvan directamente esos valores

        # si productos_comprados no contiene ningún elemento
        # se devuelve
        if not productos_comprados.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        # ---------------------------------------------
        # 2️⃣ Categorías favoritas del cliente
        # obtiene los IDs de las categorías ordenados según la frecuencia de compra
        # ---------------------------------------------
        categorias_favoritas = (
            Producto.objects.filter(id__in=productos_comprados)
            .values('categoria_id') # se selecciona la categoría asociada al producto comprado
            .annotate(total=Count('categoria_id')) # total es un campo calculado que almacena la cant de cada cat.
            .order_by('-total')
            .values_list('categoria_id', flat=True)
        )

        # si no hay categorías favorita se ejecua el metodo auxiliar y devuelve (por defecto)
        # los productos más vendidos
        if not categorias_favoritas:
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(
                limite,
                productos_excluidos=productos_comprados,
            )

        # ---------------------------------------------
        # 3️⃣ Productos recomendados (misma categoría)
        # ---------------------------------------------
        recomendaciones = (
            Producto.objects.filter(categoria_id__in=categorias_favoritas)
            .exclude(id__in=productos_comprados)
            .order_by('-stock')[:limite]
        )

        # ---------------------------------------------
        # 4️⃣ Fallback si no hay nuevos productos
        # ---------------------------------------------
        if not recomendaciones.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(
                limite,
                productos_excluidos=productos_comprados,
            )
            # si el cliente no compró nunca, se muestran los 5 productos más vendidos a nivel global

        return recomendaciones

    # este método, en lugar de utilizar todas las categorías (como el anterior) identifica
    # solamente la categoría que más compró y recomienda productos de esa categoría
    @staticmethod
    def recomendar_por_categoria_favorita(*, cliente_id, limite=5):
        """
        Recomienda productos basados únicamente en la categoría
        más comprada por el cliente.
        """

        productos_comprados = PedidoItem.objects.filter(
            # buscar todos los pedidoitem cuyo pedido 
            # pertenece a un cliente cuyo id_cliente coincide con id_cliente del parámetro
            pedido__cliente__id_cliente=cliente_id, 

            pedido__estado__in=['pagado', 'enviado', 'entregado']
        ).values_list('producto_id', flat=True) # solo devuelve producto_id, no todos los campos de PedidoItem

        # si el cliente no compró productos, por defecti, se devuelven los 5 productos más vendidos
        if not productos_comprados.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        # ---------------------------------------------
        # Categoría más comprada por el cliente
        # ---------------------------------------------
        categoria_favorita = (
            Producto.objects.filter(id__in=productos_comprados)
            .values('categoria_id') # el resultado solo va a mostrar el id de la categoria
            .annotate(total=Count('categoria_id'))
            .order_by('-total')
            .first() # obtiene el primer resultado
        )

        if not categoria_favorita:
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(
                limite,
                productos_excluidos=productos_comprados,
            )

        recomendaciones = (
            Producto.objects.filter(
                categoria_id=categoria_favorita['categoria_id']
            )
            .exclude(id__in=productos_comprados)[:limite]
        )

        # ---------------------------------------------
        # Fallback si no hay productos nuevos
        # ---------------------------------------------
        if not recomendaciones.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(
                limite,
                productos_excluidos=productos_comprados,
            )

        return recomendaciones

    @staticmethod
    def _fallback_mas_vendidos(limite, productos_excluidos=()):
        """
        Usa el resumen analítico disponible y completa los resultados con
        compras reales cuando ese resumen todavía no fue generado.
        """
        productos_ids = list(
            ProductoMasVendido.objects
            .exclude(producto_id__in=productos_excluidos)
            .values('producto_id')
            .annotate(total_vendido=Max('total_vendido'))
            .order_by('-total_vendido', 'producto_id')
            .values_list('producto_id', flat=True)[:limite]
        )

        productos_validos = set(
            Producto.objects.filter(pk__in=productos_ids)
            .values_list('pk', flat=True)
        )
        productos_ids = [
            producto_id
            for producto_id in productos_ids
            if producto_id in productos_validos
        ]

        if len(productos_ids) < limite:
            productos_ids.extend(
                PedidoItem.objects
                .filter(
                    pedido__estado__in=['pagado', 'enviado', 'entregado']
                )
                .exclude(producto_id__in=productos_excluidos)
                .exclude(producto_id__in=productos_ids)
                .values('producto_id')
                .annotate(total_vendido=Sum('cantidad'))
                .order_by('-total_vendido', 'producto_id')
                .values_list('producto_id', flat=True)[:limite - len(productos_ids)]
            )

        if not productos_ids:
            return Producto.objects.none()

        orden = Case(
            *[
                When(pk=producto_id, then=posicion)
                for posicion, producto_id in enumerate(productos_ids)
            ],
            output_field=IntegerField(),
        )
        return Producto.objects.filter(pk__in=productos_ids).order_by(orden)
