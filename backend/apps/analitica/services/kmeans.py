import numpy as np

from django.db.models import Sum

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from apps.pedidos.models import Pedido
from apps.analitica.models import ClienteSegmentado
from apps.clientes.models import Cliente


def segmentar_clientes_kmeans(
    n_clusters=3,
    random_state=42
):
    """
    Segmenta clientes utilizando K-Means.

    Variables utilizadas:

    - Total gastado histórico.
    - Cantidad de pedidos realizados.
    - Provincia (codificada mediante One-Hot Encoding).

    Incluye clientes sin compras
    con valores:
        total = 0
        pedidos = 0

    Guarda ClienteSegmentado asociado
    al Usuario correcto.

    Los clusters se renumeran automáticamente:

        0 = Inactivos / Bajo valor
        1 = Clientes medios
        2 = Clientes VIP
    """

    # =====================================================
    # 1. OBTENER CLIENTES
    # =====================================================

    clientes = Cliente.objects.select_related(
        "id_cliente"
    )

    if not clientes.exists():
        return []

    # =====================================================
    # 2. CREAR DATASET
    # =====================================================

    usuarios = []

    datos_numericos = []

    provincias = []

    # Se utilizarán luego para ordenar los clusters
    gastos = []

    pedidos_cliente = []

    for cliente in clientes:

        pedidos = Pedido.objects.filter(

            cliente=cliente,

            estado__in=[
                "pagado",
                "enviado",
                "entregado"
            ]

        )

        total = pedidos.aggregate(
            suma=Sum("total")
        )["suma"] or 0

        cantidad = pedidos.count()

        usuarios.append(
            cliente.id_cliente
        )

        gastos.append(float(total))
        pedidos_cliente.append(int(cantidad))

        datos_numericos.append(
            [
                float(total),
                int(cantidad)
            ]
        )

        provincias.append([
            cliente.provincia or "Sin provincia"
        ])

    # =====================================================
    # 3. CODIFICAR PROVINCIAS
    # =====================================================

    try:
        encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown="ignore"
        )
    except TypeError:

        encoder = OneHotEncoder(
            sparse=False,
            handle_unknown="ignore"
        )

    provincias_codificadas = encoder.fit_transform(
        provincias
    )

    # =====================================================
    # 4. UNIR VARIABLES
    # =====================================================

    X_numerico = np.array(
        datos_numericos,
        dtype=float
    )

    X = np.hstack(
        (
            X_numerico,
            provincias_codificadas
        )
    )

    # =====================================================
    # 5. AJUSTAR CANTIDAD DE CLUSTERS
    # =====================================================

    if len(X) < n_clusters:

        n_clusters = max(
            1,
            len(X)
        )

    if len(
        set(
            tuple(x)
            for x in X
        )
    ) == 1:

        n_clusters = 1

    # =====================================================
    # 6. NORMALIZACIÓN
    # =====================================================

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )

    # =====================================================
    # 7. KMEANS
    # =====================================================

    kmeans = KMeans(

        n_clusters=n_clusters,

        random_state=random_state,

        n_init=10

    )

    clusters = kmeans.fit_predict(
        X_scaled
    )

    # =====================================================
    # 8. RENOMBRAR CLUSTERS SEGÚN GASTO PROMEDIO
    # =====================================================

    estadisticas = {}

    for cluster, gasto, cantidad in zip(
        clusters,
        gastos,
        pedidos_cliente
    ):

        if cluster not in estadisticas:

            estadisticas[cluster] = {
                "gasto": 0,
                "pedidos": 0,
                "clientes": 0
            }

        estadisticas[cluster]["gasto"] += gasto
        estadisticas[cluster]["pedidos"] += cantidad
        estadisticas[cluster]["clientes"] += 1

    promedios = []

    for cluster, datos in estadisticas.items():

        promedio_gasto = (
            datos["gasto"] /
            datos["clientes"]
        )

        promedios.append(
            (
                cluster,
                promedio_gasto
            )
        )

    # Menor gasto -> Bajo valor
    # Mayor gasto -> VIP
    promedios.sort(
        key=lambda x: x[1]
    )

    mapa_clusters = {}

    for nuevo_cluster, (
        cluster_original,
        _
    ) in enumerate(promedios):

        mapa_clusters[
            cluster_original
        ] = nuevo_cluster

    clusters = np.array(
        [
            mapa_clusters[c]
            for c in clusters
        ]
    )

    # =====================================================
    # 9. LIMPIAR RESULTADOS ANTERIORES
    # =====================================================

    ClienteSegmentado.objects.all().delete()

    # =====================================================
    # 10. PREPARAR INSERT MASIVO
    # =====================================================

    segmentos = []

    for usuario, cluster in zip(
        usuarios,
        clusters
    ):

        segmentos.append(

            ClienteSegmentado(

                cliente=usuario,

                cluster=int(cluster)

            )

        )

    # =====================================================
    # 11. INSERTAR
    # =====================================================

    ClienteSegmentado.objects.bulk_create(

        segmentos,

        batch_size=500

    )

    print(
        "Clientes analizados:",
        len(usuarios)
    )

    print(
        "Variables utilizadas:"
    )

    print("- Total gastado")
    print("- Cantidad de pedidos")
    print("- Provincia (One-Hot Encoding)")

    print(
        "Cantidad de provincias:",
        len(encoder.categories_[0])
    )

    print()

    print("Renumeración de clusters:")

    etiquetas = [
        "Inactivos / Bajo valor",
        "Clientes medios",
        "Clientes VIP"
    ]

    for cluster_original, nuevo in mapa_clusters.items():

        promedio = dict(promedios)[cluster_original]

        print(
            f"Cluster {cluster_original}"
            f" -> {nuevo}"
            f" ({etiquetas[nuevo]})"
            f" | gasto promedio: ${promedio:,.2f}"
        )

    print()

    print(
        "Clusters finales:",
        set(clusters)
    )

    return segmentos