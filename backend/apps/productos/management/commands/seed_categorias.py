from django.core.management.base import BaseCommand
from django.db import connection

from apps.productos.models import Categoria


class Command(BaseCommand):

    help = "Carga las categorías iniciales del ecommerce una única vez"


    def handle(self, *args, **kwargs):

        # ==========================================
        # EVITAR DUPLICADOS
        # ==========================================

        if Categoria.objects.exists():

            self.stdout.write(
                self.style.WARNING(
                    "Las categorías ya existen. No se realizó ninguna carga."
                )
            )

            return


        categorias = [

            ("Aceites",
             "Aceites comestibles para cocinar, condimentar y preparar todo tipo de comidas."),

            ("Aderezos",
             "Mayonesas, mostazas, ketchup, salsas y condimentos para acompañar tus comidas."),

            ("Bebidas",
             "Gaseosas, jugos, aguas, bebidas energéticas y refrescos para toda ocasión."),

            ("Frescos",
             "Productos frescos seleccionados diariamente para garantizar calidad y sabor."),

            ("Mascotas",
             "Alimentos, accesorios y productos de cuidado e higiene para mascotas."),

            ("Golosinas",
             "Dulces, chocolates, caramelos y snacks para disfrutar en cualquier momento."),

            ("Limpieza",
             "Productos destinados a la limpieza y desinfección del hogar y diferentes superficies."),

            ("Lácteos",
             "Leches, yogures, quesos y derivados lácteos frescos y nutritivos."),

            ("Accesorios de limpieza",
             "Escobas, esponjas, guantes y artículos complementarios para tareas de limpieza."),

            ("Insecticidas",
             "Productos diseñados para eliminar insectos y proteger los ambientes del hogar."),

            ("Librería",
             "Artículos escolares, de oficina y papelería para estudio, trabajo y organización."),

            ("Arroz, Legumbres y Sémolas",
             "Variedad de arroz, lentejas, porotos, garbanzos y sémolas para múltiples preparaciones."),

            ("Harinas",
             "Harinas tradicionales y especiales para cocina, panadería y repostería."),

            ("Leches en Polvo",
             "Leches en polvo nutritivas para consumo diario y preparación de bebidas o recetas."),

            ("Pastas Secas y Salsas",
             "Fideos, pastas secas y salsas listas para acompañar tus comidas favoritas."),

            ("Pastas sin TACC",
             "Pastas libres de gluten aptas para personas con intolerancia al gluten."),

            ("Repostería",
             "Ingredientes y productos ideales para tortas, postres y preparaciones dulces."),

            ("Panadería",
             "Panes, facturas y productos horneados frescos para cada momento del día."),

            ("Perfumería",
             "Productos de cuidado personal, higiene y belleza para toda la familia."),

            ("Saludables",
             "Productos naturales, bajos en azúcar y opciones pensadas para una alimentación saludable."),

        ]


        # ==========================================
        # REINICIAR AUTOINCREMENTO SQLITE
        # ==========================================

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name='productos_categoria';"
            )


        # ==========================================
        # INSERTAR CATEGORIAS
        # ==========================================

        Categoria.objects.bulk_create(
            [
                Categoria(
                    nombre=nombre,
                    descripcion=descripcion
                )
                for nombre, descripcion in categorias
            ]
        )


        self.stdout.write(
            self.style.SUCCESS(
                "Se cargaron 20 categorías correctamente iniciando desde ID 1."
            )
        )