from django.db.models import Count
from apps.pedidos.models import PedidoItem
from apps.productos.models import Producto
from apps.analitica.models import ProductoMasVendido


class RecomendacionPersonalizadaService:
    """
    Servicio de recomendaciones personalizadas basado en:
    - historial de compras del cliente
    - categorías favoritas
    - fallback a productos más vendidos (analítica)
    """

    @staticmethod
    def recomendar_productos_por_cliente(*, cliente_id, limite=5):
        """
        Recomienda productos según el historial de compras del cliente.
        Prioriza productos de categorías frecuentes y excluye los ya comprados.
        """

        # ---------------------------------------------
        # 1️⃣ Productos comprados por el cliente
        # ---------------------------------------------
        productos_comprados = PedidoItem.objects.filter(
            pedido__cliente__id_cliente=cliente_id,
            pedido__estado__in=['pagado', 'enviado', 'entregado']
        ).values_list('producto_id', flat=True)

        if not productos_comprados.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        # ---------------------------------------------
        # 2️⃣ Categorías favoritas del cliente
        # ---------------------------------------------
        categorias_favoritas = (
            Producto.objects.filter(id__in=productos_comprados)
            .values('categoria_id')
            .annotate(total=Count('categoria_id'))
            .order_by('-total')
            .values_list('categoria_id', flat=True)
        )

        if not categorias_favoritas:
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

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
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        return recomendaciones

    @staticmethod
    def recomendar_por_categoria_favorita(*, cliente_id, limite=5):
        """
        Recomienda productos basados únicamente en la categoría
        más comprada por el cliente.
        """

        productos_comprados = PedidoItem.objects.filter(
            pedido__cliente__id_cliente=cliente_id,
            pedido__estado__in=['pagado', 'enviado', 'entregado']
        ).values_list('producto_id', flat=True)

        if not productos_comprados.exists():
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        # ---------------------------------------------
        # Categoría más comprada por el cliente
        # ---------------------------------------------
        categoria_favorita = (
            Producto.objects.filter(id__in=productos_comprados)
            .values('categoria_id')
            .annotate(total=Count('categoria_id'))
            .order_by('-total')
            .first()
        )

        if not categoria_favorita:
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

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
            return RecomendacionPersonalizadaService._fallback_mas_vendidos(limite)

        return recomendaciones

    @staticmethod
    def _fallback_mas_vendidos(limite):
        """
        Recomendación alternativa basada en analítica:
        productos más vendidos globalmente.
        """

        productos_ids = (
            ProductoMasVendido.objects
            .order_by('-total_vendido')
            .values_list('producto_id', flat=True)[:limite]
        )

        return Producto.objects.filter(id__in=productos_ids)
