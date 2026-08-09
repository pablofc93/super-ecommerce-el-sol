"""
Funciones auxiliares para la generación de datos de prueba.
"""

import random


from utils.seed.ciudades import CIUDADES

from utils.seed.provincias import PROVINCIAS



def generar_ubicacion():
    """
    Genera una provincia y ciudad coherentes.
    """

    provincia = random.choice(
        PROVINCIAS
    )


    ciudades = CIUDADES.get(
        provincia
    )


    if ciudades:

        ciudad = random.choice(
            ciudades
        )

    else:

        ciudad = provincia



    return provincia, ciudad



def generar_codigo_postal():

    """
    Genera códigos postales argentinos simples.
    """

    return str(
        random.randint(
            1000,
            9999
        )
    )



def generar_telefono():

    """
    Genera teléfonos argentinos ficticios.
    """

    prefijos = [

        "11",
        "221",
        "341",
        "351",
        "381",
        "388",

    ]


    prefijo = random.choice(
        prefijos
    )


    numero = random.randint(
        1000000,
        9999999
    )


    return f"{prefijo}{numero}"