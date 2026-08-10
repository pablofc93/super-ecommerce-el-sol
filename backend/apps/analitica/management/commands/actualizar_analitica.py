import time

from django.core.management.base import BaseCommand

# ==========================================
# Servicios
# ==========================================
from apps.analitica.services.demanda import (
    actualizar_categorias_mas_movidas,
    actualizar_demanda_productos,
)
from apps.analitica.services.apriori import calcular_reglas_asociacion
from apps.analitica.services.kmeans import segmentar_clientes_kmeans
from apps.analitica.tasks import limpiar_datos


class Command(BaseCommand):

    help = "Actualiza metricas de analitica y mineria de datos"

    def handle(self, *args, **options):
        inicio_total = time.perf_counter()

        self.stdout.write("")
        self.stdout.write("=" * 65)
        self.stdout.write(self.style.SUCCESS("INICIANDO ACTUALIZACION DE ANALITICA"))
        self.stdout.write("=" * 65)

        tiempos = {}

        # =====================================================
        # 1. LIMPIEZA
        # =====================================================
        inicio = time.perf_counter()

        limpiar_datos()

        tiempos["Limpieza"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(f"Datos limpiados ({tiempos['Limpieza']:.2f}s)")
        )

        # =====================================================
        # 2. PRODUCTOS MAS VENDIDOS
        # =====================================================
        inicio = time.perf_counter()

        actualizar_demanda_productos()

        tiempos["Productos"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(
                f"Productos mas vendidos actualizados ({tiempos['Productos']:.2f}s)"
            )
        )

        # =====================================================
        # 3. CATEGORIAS
        # =====================================================
        inicio = time.perf_counter()

        actualizar_categorias_mas_movidas()

        tiempos["Categorias"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(
                f"Categorias mas movidas actualizadas ({tiempos['Categorias']:.2f}s)"
            )
        )

        # =====================================================
        # 4. APRIORI
        # =====================================================
        inicio = time.perf_counter()

        reglas = calcular_reglas_asociacion(
            soporte_minimo=0.0003,
            confianza_minima=0.15,
            lift_minimo=0.80,
            max_reglas=500,
        )

        tiempos["Apriori"] = time.perf_counter() - inicio

        if reglas:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Reglas de asociacion generadas: {len(reglas)} "
                    f"({tiempos['Apriori']:.2f}s)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"No se generaron reglas de asociacion ({tiempos['Apriori']:.2f}s)"
                )
            )

        # =====================================================
        # 5. KMEANS
        # =====================================================
        inicio = time.perf_counter()

        segmentos = segmentar_clientes_kmeans(n_clusters=3)

        tiempos["KMeans"] = time.perf_counter() - inicio

        if segmentos:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Clientes segmentados: {len(segmentos)} ({tiempos['KMeans']:.2f}s)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"No se pudo ejecutar KMeans ({tiempos['KMeans']:.2f}s)"
                )
            )

        # =====================================================
        # RESUMEN FINAL
        # =====================================================
        tiempo_total = time.perf_counter() - inicio_total

        self.stdout.write("")
        self.stdout.write("=" * 65)
        self.stdout.write(self.style.SUCCESS("RESUMEN DE EJECUCION"))
        self.stdout.write("=" * 65)

        for nombre, segundos in tiempos.items():
            porcentaje = (segundos / tiempo_total) * 100

            self.stdout.write(
                f"{nombre:<15}{segundos:>8.2f} s   ({porcentaje:>5.1f}%)"
            )

        self.stdout.write("-" * 65)

        self.stdout.write(
            self.style.SUCCESS(f"Tiempo total: {tiempo_total:.2f} segundos")
        )

        self.stdout.write(
            self.style.SUCCESS("Analitica actualizada correctamente")
        )

        self.stdout.write("=" * 65)
        self.stdout.write("")