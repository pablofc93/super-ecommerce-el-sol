from django.core.management.base import BaseCommand
import time

# ==========================================
# Servicios
# ==========================================
from apps.analitica.services.demanda import (
    actualizar_demanda_productos,
    actualizar_categorias_mas_movidas,
)

from apps.analitica.services.apriori import (
    calcular_reglas_asociacion,
)

from apps.analitica.services.kmeans import (
    segmentar_clientes_kmeans,
)

from apps.analitica.tasks import limpiar_datos


class Command(BaseCommand):
    help = "Actualiza métricas de analítica y minería de datos"

    def handle(self, *args, **options):

        inicio_total = time.perf_counter()

        self.stdout.write("")
        self.stdout.write("=" * 65)
        self.stdout.write(
            self.style.SUCCESS(
                "🔄 INICIANDO ACTUALIZACIÓN DE ANALÍTICA"
            )
        )
        self.stdout.write("=" * 65)

        tiempos = {}

        # =====================================================
        # 1. LIMPIEZA
        # =====================================================
        inicio = time.perf_counter()

        limpiar_datos()

        tiempos["Limpieza"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ Datos limpiados "
                f"({tiempos['Limpieza']:.2f}s)"
            )
        )

        # =====================================================
        # 2. PRODUCTOS MÁS VENDIDOS
        # =====================================================
        inicio = time.perf_counter()

        actualizar_demanda_productos()

        tiempos["Productos"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ Productos más vendidos actualizados "
                f"({tiempos['Productos']:.2f}s)"
            )
        )

        # =====================================================
        # 3. CATEGORÍAS
        # =====================================================
        inicio = time.perf_counter()

        actualizar_categorias_mas_movidas()

        tiempos["Categorías"] = time.perf_counter() - inicio

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ Categorías más movidas actualizadas "
                f"({tiempos['Categorías']:.2f}s)"
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
                    f"✔ Reglas de asociación generadas: {len(reglas)} "
                    f"({tiempos['Apriori']:.2f}s)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ No se generaron reglas de asociación "
                    f"({tiempos['Apriori']:.2f}s)"
                )
            )

        # =====================================================
        # 5. KMEANS
        # =====================================================
        inicio = time.perf_counter()

        segmentos = segmentar_clientes_kmeans(
            n_clusters=3
        )

        tiempos["KMeans"] = time.perf_counter() - inicio

        if segmentos:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✔ Clientes segmentados: {len(segmentos)} "
                    f"({tiempos['KMeans']:.2f}s)"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ No se pudo ejecutar KMeans "
                    f"({tiempos['KMeans']:.2f}s)"
                )
            )

        # =====================================================
        # RESUMEN FINAL
        # =====================================================
        tiempo_total = time.perf_counter() - inicio_total

        self.stdout.write("")
        self.stdout.write("=" * 65)
        self.stdout.write(
            self.style.SUCCESS(
                "📊 RESUMEN DE EJECUCIÓN"
            )
        )
        self.stdout.write("=" * 65)

        for nombre, segundos in tiempos.items():

            porcentaje = (
                segundos / tiempo_total
            ) * 100

            self.stdout.write(
                f"{nombre:<15}"
                f"{segundos:>8.2f} s"
                f"   ({porcentaje:>5.1f}%)"
            )

        self.stdout.write("-" * 65)

        self.stdout.write(
            self.style.SUCCESS(
                f"⏱ Tiempo total: {tiempo_total:.2f} segundos"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "✅ Analítica actualizada correctamente"
            )
        )

        self.stdout.write("=" * 65)
        self.stdout.write("")