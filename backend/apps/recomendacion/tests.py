from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.clientes.models import Cliente
from apps.pedidos.models import Pedido, PedidoItem
from apps.productos.models import Categoria, Producto
from apps.recomendacion.services.personalizadas import (
    RecomendacionPersonalizadaService,
)


class RecomendacionesPorClienteTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.cliente = user_model.objects.create_user(
            username="cliente-recomendaciones",
            email="cliente-recomendaciones@example.com",
            password="test-password",
            tipo_usuario="cliente",
        )
        self.otro_cliente = user_model.objects.create_user(
            username="otro-cliente-recomendaciones",
            email="otro-cliente-recomendaciones@example.com",
            password="test-password",
            tipo_usuario="cliente",
        )
        self.admin = user_model.objects.create_user(
            username="admin-recomendaciones",
            email="admin-recomendaciones@example.com",
            password="test-password",
            tipo_usuario="admin",
        )
        for user in (self.cliente, self.otro_cliente, self.admin):
            Cliente.objects.get_or_create(id_cliente=user)
        self.client = APIClient()
        self.url = reverse(
            "recomendacion:recomendacion-por-cliente",
            kwargs={"id_cliente": self.cliente.pk},
        )

    @patch(
        "apps.recomendacion.views.RecomendacionPersonalizadaService."
        "recomendar_productos_por_cliente",
        return_value=[],
    )
    def test_cliente_autenticado_obtiene_sus_recomendaciones(self, recomendar):
        self.client.force_authenticate(user=self.cliente)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        recomendar.assert_called_once_with(cliente_id=self.cliente.pk)

    @patch(
        "apps.recomendacion.views.RecomendacionPersonalizadaService."
        "recomendar_productos_por_cliente",
    )
    def test_cliente_no_puede_consultar_recomendaciones_de_otro(self, recomendar):
        self.client.force_authenticate(user=self.otro_cliente)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        recomendar.assert_not_called()

    @patch(
        "apps.recomendacion.views.RecomendacionPersonalizadaService."
        "recomendar_productos_por_cliente",
        return_value=[],
    )
    def test_administrador_puede_consultar_recomendaciones_de_un_cliente(self, recomendar):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        recomendar.assert_called_once_with(cliente_id=self.cliente.pk)

    def test_usuario_no_autenticado_no_puede_consultar_recomendaciones(self):
        response = self.client.get(self.url)

        self.assertIn(response.status_code, (401, 403))


class RecomendacionFallbackTests(TestCase):
    def test_usa_pedidos_pagados_si_no_hay_resumen_analitico(self):
        user_model = get_user_model()
        cliente_usuario = user_model.objects.create_user(
            username="cliente-fallback-recomendaciones",
            email="cliente-fallback@example.com",
            password="test-password",
        )
        otro_usuario = user_model.objects.create_user(
            username="otro-fallback-recomendaciones",
            email="otro-fallback@example.com",
            password="test-password",
        )
        cliente = Cliente.objects.create(id_cliente=cliente_usuario)
        otro_cliente = Cliente.objects.create(id_cliente=otro_usuario)
        categoria_comprada = Categoria.objects.create(nombre="Categoria comprada")
        categoria_popular = Categoria.objects.create(nombre="Categoria popular")
        producto_comprado = Producto.objects.create(
            categoria=categoria_comprada,
            nombre="Producto ya comprado",
            precio="10.00",
        )
        producto_popular = Producto.objects.create(
            categoria=categoria_popular,
            nombre="Producto popular",
            precio="20.00",
        )
        pedido_cliente = Pedido.objects.create(cliente=cliente, estado="pagado")
        PedidoItem.objects.create(
            pedido=pedido_cliente,
            producto=producto_comprado,
            cantidad=1,
            precio_unitario="10.00",
        )
        pedido_otro_cliente = Pedido.objects.create(
            cliente=otro_cliente,
            estado="pagado",
        )
        PedidoItem.objects.create(
            pedido=pedido_otro_cliente,
            producto=producto_popular,
            cantidad=3,
            precio_unitario="20.00",
        )

        recomendaciones = (
            RecomendacionPersonalizadaService
            .recomendar_productos_por_cliente(
                cliente_id=cliente_usuario.pk,
            )
        )

        self.assertEqual(list(recomendaciones), [producto_popular])
