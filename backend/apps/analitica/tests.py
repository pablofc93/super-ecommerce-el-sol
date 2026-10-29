from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import ReglasAsociacionView


class ReglasAsociacionViewTests(TestCase):
    def test_get_does_not_write_report_history(self):
        request = APIRequestFactory().get(
            '/api/analitica/reglas-asociacion/',
            HTTP_HOST='localhost'
        )
        force_authenticate(
            request,
            user=SimpleNamespace(
                is_authenticated=True,
                is_staff=True,
                tipo_usuario='admin'
            )
        )

        with patch(
            'apps.analitica.views.guardar_reporte'
        ) as guardar_reporte:
            response = ReglasAsociacionView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        guardar_reporte.assert_not_called()
