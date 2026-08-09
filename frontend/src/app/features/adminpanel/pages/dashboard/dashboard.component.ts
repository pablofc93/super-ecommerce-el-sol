import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdminDashboardService } from '../../services/admin-dashboard.service';

import { KpiCardComponent } from '../../components/kpi-card/kpi-card.component';
import { GraficoBarComponent } from '../../components/grafico-bar/grafico-bar.component';
import { GraficoPieComponent } from '../../components/grafico-pie/grafico-pie.component';

type DashboardTab =
  | 'productos'
  | 'categorias'
  | 'clientes'
  | 'pedidos'
  | 'reglas'
  | 'provincias'
  | 'ventas';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    KpiCardComponent,
    GraficoBarComponent,
    GraficoPieComponent,
  ],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  data: any = null;
  cargando = true;

  // ================= KPIs =================
  totalVentas = 0;
  cantidadPedidos = 0;

  // ================= PRODUCTOS =================
  productosLabels: string[] = [];
  productosData: number[] = [];

  // ================= CATEGORÍAS =================
  categoriasLabels: string[] = [];
  categoriasData: number[] = [];

  // ================= CLIENTES =================
  clientesLabels: string[] = [];
  clientesData: number[] = [];
  clientesColors: string[] = [];
  clientesExtraInfo: any[] = [];

  // ================= PEDIDOS =================
  estadosLabels: string[] = [];
  estadosData: number[] = [];

  // ================= REGLAS =================
  reglasLabels: string[] = [];
  reglasConfianzaData: number[] = [];
  reglasLiftData: number[] = [];

  // ================= DEMANDA =================
  ventasLabels: string[] = [];
  ventasData: number[] = [];

  // ================= INGRESOS =================
  ingresosLabels: string[] = [];
  ingresosData: number[] = [];

  // ================= TABS =================
  tabActivo: DashboardTab = 'productos';

  // ================= PROVINCIAS =================
  provinciasLabels: string[] = [];
  clientesProvinciaData: number[] = [];
  ventasProvinciaLabels: string[] = [];
  ventasProvinciaData: number[] = [];
  ticketProvinciaData: number[] = [];
  ticketProvinciaLabels: string[] = [];

  tabs: { key: DashboardTab; label: string; icon: string }[] = [
    { key: 'productos', label: 'Productos', icon: 'bi-box-seam' },
    { key: 'categorias', label: 'Categorías', icon: 'bi-grid' },
    { key: 'clientes', label: 'Clientes', icon: 'bi-people' },
    { key: 'pedidos', label: 'Pedidos', icon: 'bi-receipt' },
    { key: 'reglas', label: 'Reglas', icon: 'bi-robot' },
    { key: 'ventas', label: 'Ventas', icon: 'bi-cash-stack' },
    { key: 'provincias', label: 'Provincias', icon: 'bi-geo-alt' },
  ];

  constructor(private dashboardService: AdminDashboardService) {}

  ngOnInit(): void {
    this.dashboardService.obtenerDashboardCompleto().subscribe((res) => {
      this.data = res;
      this.mapearDatos();
      this.cargando = false;
    });
  }

  // ================= HELPERS =================

  getClusterLabel(cluster: number): string {
    switch (cluster) {
      case 0:
        return 'Inactivos / Bajo valor';
      case 1:
        return 'Clientes medios';
      case 2:
        return 'Clientes VIP';
      default:
        return 'Sin clasificar';
    }
  }

  getClusterColor(cluster: number): string {
    switch (cluster) {
      case 0:
        return '#36A2EB';
      case 1:
        return '#FFCE56';
      case 2:
        return '#FF6384';
      default:
        return '#999';
    }
  }

  mapearDatos() {
    if (!this.data) return;

    const meses = [
      'Ene',
      'Feb',
      'Mar',
      'Abr',
      'May',
      'Jun',
      'Jul',
      'Ago',
      'Sep',
      'Oct',
      'Nov',
      'Dic',
    ];

    // ================= PRODUCTOS =================
    this.productosLabels = this.data.productos.map(
      (p: any) => p.nombre_producto,
    );

    this.productosData = this.data.productos.map(
      (p: any) => p.total_vendido,
    );

    // ================= CATEGORÍAS =================
    this.categoriasLabels = this.data.categorias.map(
      (c: any) => c.nombre_categoria,
    );

    this.categoriasData = this.data.categorias.map(
      (c: any) => c.total_movimiento,
    );

    // ================= CLIENTES =================
    const clusterMap: any = {};
    const clusterStats: any = {};

    this.data.clientes.forEach((c: any) => {
      const cluster = c.cluster;

      clusterMap[cluster] = (clusterMap[cluster] || 0) + 1;

      if (!clusterStats[cluster]) {
        clusterStats[cluster] = {
          total_gasto: 0,
          total_pedidos: 0,
          cantidad: 0,
        };
      }

      clusterStats[cluster].total_gasto += c.total_gasto || 0;
      clusterStats[cluster].total_pedidos += c.total_pedidos || 0;
      clusterStats[cluster].cantidad += 1;
    });

    const clustersOrdenados = Object.keys(clusterMap)
      .map(Number)
      .sort((a, b) => b - a);

    this.clientesLabels = clustersOrdenados.map((c) =>
      this.getClusterLabel(c),
    );

    this.clientesData = clustersOrdenados.map((c) => clusterMap[c]);

    this.clientesColors = clustersOrdenados.map((c) =>
      this.getClusterColor(c),
    );

    this.clientesExtraInfo = clustersOrdenados.map((c) => {
      const stats = clusterStats[c];
    
      return {
        promedio_gasto: Number(
          (stats.total_gasto / stats.cantidad).toFixed(2)
        ),
        promedio_pedidos: Number(
          (stats.total_pedidos / stats.cantidad).toFixed(2)
        ),
      };
    });

    // ================= KPIs =================
    this.totalVentas = Number(this.data.kpis.ventas_totales || 0);
    this.cantidadPedidos = Number(this.data.kpis.total_pedidos || 0);

    // ================= PEDIDOS =================
    this.estadosLabels = this.data.pedidosPorEstado.map(
      (p: any) => p.estado,
    );

    this.estadosData = this.data.pedidosPorEstado.map(
      (p: any) => p.total,
    );

    // ================= REGLAS =================
    const reglas = this.data.reglas || [];

    this.reglasLabels = reglas.map(
      (r: any) => `${r.base} → ${r.recomendado}`,
    );

    this.reglasConfianzaData = reglas.map(
      (r: any) => r.confianza,
    );

    this.reglasLiftData = reglas.map(
      (r: any) => r.lift,
    );

    // ================= DEMANDA =================
    const ventasOrdenadas = [...this.data.ventasMensuales].sort(
      (a: any, b: any) =>
        Number(b.total_vendido) - Number(a.total_vendido),
    );

    this.ventasLabels = ventasOrdenadas.map(
      (v: any) => meses[v.pedido__fecha__month - 1],
    );

    this.ventasData = ventasOrdenadas.map(
      (v: any) => Number(v.total_vendido),
    );

    // ================= INGRESOS =================
    const ingresosOrdenados = [...this.data.ventasIngresosMensuales]
      .filter((v: any) => v.mes != null)
      .sort((a: any, b: any) => a.mes - b.mes);

    this.ingresosLabels = ingresosOrdenados.map(
      (v: any) => meses[v.mes - 1],
    );

    this.ingresosData = ingresosOrdenados.map(
      (v: any) => Number(v.total_ingresos || 0),
    );

    // ================= PROVINCIAS =================
    const provincias = this.data.kpisProvincia || [];

    this.provinciasLabels = provincias.map(
      (p: any) => p.provincia || 'Sin provincia',
    );

    this.clientesProvinciaData = provincias.map(
      (p: any) => Number(p.cantidad_clientes || 0),
    );

    const provinciasPorTicket = [...provincias].sort(
      (a: any, b: any) =>
        Number(b.ticket_promedio || 0) -
        Number(a.ticket_promedio || 0),
    );

    this.ticketProvinciaLabels = provinciasPorTicket.map(
      (p: any) => p.provincia || 'Sin provincia',
    );

    this.ticketProvinciaData = provinciasPorTicket.map(
      (p: any) => Number(p.ticket_promedio || 0),
    );

    const provinciasPorVentas = [...provincias].sort(
      (a: any, b: any) =>
        Number(b.ventas_totales || 0) -
        Number(a.ventas_totales || 0),
    );

    this.ventasProvinciaLabels = provinciasPorVentas.map(
      (p: any) => p.provincia || 'Sin provincia',
    );

    this.ventasProvinciaData = provinciasPorVentas.map(
      (p: any) => Number(p.ventas_totales || 0),
    );
  }

  cambiarTab(tab: DashboardTab) {
    this.tabActivo = tab;
  }
}