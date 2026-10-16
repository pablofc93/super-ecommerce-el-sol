import numpy as np
from django.db.models import Sum
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from apps.pedidos.models import Pedido
from apps.analitica.models import ClienteSegmentado
from apps.clientes.models import Cliente


def segmentar_clientes_kmeans(n_clusters=3, random_state=42):
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
    # se obtienen también los usuarios asociados al cliente junto con toda su información
    # =====================================================
    clientes = Cliente.objects.select_related("id_cliente")
    if not clientes.exists():
        return []

    # =====================================================
    # 2. CREAR ESTRUCTURA DEL DATASET
    # =====================================================
    usuarios = []
    datos_numericos = [] # almacena total gastado y cantidad de pedidos
    provincias = [] # almacena la provincia de cada cliente

    # Se utilizarán luego para ordenar los clusters
    gastos = [] # almacena el gasto total de cada cliente
    pedidos_cliente = [] # almacena los id de los pedidos de cada cliente

    for cliente in clientes:
        # consultar la bd para obtener los pedidos válidos de los clientes
        pedidos = Pedido.objects.filter(
            cliente=cliente,
            estado__in=["pagado", "enviado", "entregado"]
        )
        # se suman los v. del campo "total" y mostrar en el campo creado "suma"
        total = pedidos.aggregate(suma=Sum("total"))["suma"] or 0
        cantidad = pedidos.count()

        usuarios.append(cliente.id_cliente) # se guardan los usuarios en la lista
        gastos.append(float(total)) # se guardan los gastos
        pedidos_cliente.append(int(cantidad)) # se guarda la cantidad de pedidos por cliente
        datos_numericos.append([float(total), int(cantidad)])
        provincias.append([cliente.provincia or "Sin provincia"])

    # =====================================================
    # 3. CODIFICAR PROVINCIAS
    # =====================================================
    try:
        # se crea un objeto del tipo OneHotEncoder para saber cuales serán las pronvincias que se convertirán a números
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    except TypeError:
        encoder = OneHotEncoder(sparse=False, handle_unknown="ignore") # depende de la versión, si se ejecuta lo del try o lo del except

    # encoder.fit analiza los datos que están en provincias[]
    # _transform utiliza los elementos de la lista para convertir cada provincia
    # en valores numéricos. ej: Jujuy->[0,1,0], Salta->[0,0,1], Tucumán->[1,0,0]
    provincias_codificadas = encoder.fit_transform(provincias)

    # =====================================================
    # 4. UNIR VARIABLES
    # =====================================================
    X_numerico = np.array(datos_numericos, dtype=float) # se convierten los elementos de datos_numericos en float y se almacenan como elementos de un array de numpy
    X = np.hstack((X_numerico, provincias_codificadas)) # se colocal mas matrices de x_numerico y provincias_codificadas juntas, y se las almacena en X

    # =====================================================
    # 5. AJUSTAR CANTIDAD DE CLUSTERS
    # =====================================================

    # len(x) representa la cantidad de clientes, entonces si la cantidad de clientes es menor al número de clusters:
    # entonces el número de clusters se reduce al número de clientes
    if len(X) < n_clusters:
        n_clusters = max(1, len(X))

    # set elimina elementos repetidos de la tupla generada
    if len(set(tuple(x) for x in X)) == 1:
        n_clusters = 1

    # =====================================================
    # 6. NORMALIZACIÓN
    # se estandarizan las variables que están en X de modo que si hay valores muy grandes estos no afecten al resultado del cluster
    # =====================================================
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # =====================================================
    # 7. KMEANS - a partir de aqui inicializa el algoritmo
    # se crea un objeto de la clase KMeans que recibe como parámetro:
    # el número de clusters, la leatoriedad de kmeans y la cantidad de puntos utilizados como centroides
    # =====================================================
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    clusters = kmeans.fit_predict(X_scaled) # se obtienen los clusters. fit: aprende los clusters a partir de los datos, predict: asigna a cada cliente un cluster

    # =====================================================
    # 8. RENOMBRAR CLUSTERS SEGÚN GASTO PROMEDIO
    # =====================================================
    estadisticas = {}
    for cluster, gasto, cantidad in zip(clusters, gastos, pedidos_cliente):
        if cluster not in estadisticas:
            estadisticas[cluster] = {"gasto": 0, "pedidos": 0, "clientes": 0}
        estadisticas[cluster]["gasto"] += gasto
        estadisticas[cluster]["pedidos"] += cantidad
        estadisticas[cluster]["clientes"] += 1 # cada vez que se encuentra un cliente perteneciente a ese cluster, se lo cuenta

    promedios = []
    for cluster, datos in estadisticas.items(): # .items permite recorrer el diccionari accediendo a su clave+valor simultáneamente
        promedio_gasto = datos["gasto"] / datos["clientes"]
        promedios.append((cluster, promedio_gasto))

    # Menor gasto -> Bajo valor
    # Mayor gasto -> VIP
    promedios.sort(key=lambda x: x[1]) # ordena los clusters de menor a mayor

    # se crea otro diccionario
    # su objetivo es establecer una correspondencia entre:
    # cluster original -> nuevo cluster
    mapa_clusters = {}
    for nuevo_cluster, (cluster_original, _) in enumerate(promedios):
        mapa_clusters[cluster_original] = nuevo_cluster

    clusters = np.array([mapa_clusters[c] for c in clusters])

    # =====================================================
    # 9. LIMPIAR RESULTADOS ANTERIORES - hasta aqui
    # =====================================================
    ClienteSegmentado.objects.all().delete()

    # =====================================================
    # 10. PREPARAR INSERT MASIVO
    # =====================================================
    segmentos = []
    for usuario, cluster in zip(usuarios, clusters):
        segmentos.append(ClienteSegmentado(cliente=usuario, cluster=int(cluster)))

    # =====================================================
    # 11. INSERTAR
    # =====================================================
    ClienteSegmentado.objects.bulk_create(segmentos, batch_size=500)

    print("Clientes analizados:", len(usuarios))
    print("Variables utilizadas:")
    print("- Total gastado")
    print("- Cantidad de pedidos")
    print("- Provincia (One-Hot Encoding)")
    print("Cantidad de provincias:", len(encoder.categories_[0]))
    print()
    print("Renumeración de clusters:")

    etiquetas = ["Inactivos / Bajo valor", "Clientes medios", "Clientes VIP"]
    for cluster_original, nuevo in mapa_clusters.items():
        promedio = dict(promedios)[cluster_original]
        print(
            f"Cluster {cluster_original}"
            f" -> {nuevo}"
            f" ({etiquetas[nuevo]})"
            f" | gasto promedio: ${promedio:,.2f}"
        )

    print()
    print("Clusters finales:", set(clusters))

    return segmentos