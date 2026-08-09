export interface AnaliticaResumen {
  productos_analizados: number;
  categorias_analizadas: number;
  clientes_segmentados: number;
  reglas_asociacion: number;
}

export interface ProductoMasVendido {
  producto_id: number;
  nombre_producto: string;
  total_vendido: number;
}

export interface CategoriaMasMovida {
  categoria_id: number;
  nombre_categoria: string;
  total_movimiento: number;
}

export interface ClienteSegmentado {
  cliente: number;
  cluster: number;
}

export interface ReglaAsociacion {
  base: string;
  recomendado: string;
  soporte: number;
  confianza: number;
  lift: number;
}

export interface PedidoAdmin {
  id_pedido: number;
  total: number;
  estado: string;
  cliente: number;
}

export interface VentaMensual {
  pedido__fecha__month: number;
  total_vendido: number;
}

export interface KpisReales {
  total_productos: number;
  total_categorias: number;
  categorias_activas: number;
  total_clientes: number;
  total_pedidos: number;
  ventas_totales: number;
}

export interface PedidoPorEstado {
  estado: string;
  total: number;
}

export interface IngresoMensual {
  mes: number;
  total_ingresos: number;
}

export interface KpiProvincia {
  provincia: string;
  cantidad_clientes: number;
  ventas_totales: number;
  ticket_promedio: number;
}

export interface DashboardCompleto {
  resumen: AnaliticaResumen;
  kpis: KpisReales;

  productos: ProductoMasVendido[];
  categorias: CategoriaMasMovida[];
  clientes: ClienteSegmentado[];
  reglas: ReglaAsociacion[];

  pedidosPorEstado: PedidoPorEstado[];

  ventasMensuales: VentaMensual[];
  ventasIngresosMensuales: IngresoMensual[];

  kpisProvincia: KpiProvincia[];
}