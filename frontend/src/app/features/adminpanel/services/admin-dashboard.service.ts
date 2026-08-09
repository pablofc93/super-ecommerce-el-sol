import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { forkJoin, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import {
  DashboardCompleto,
  AnaliticaResumen,
  ProductoMasVendido,
  CategoriaMasMovida,
  ClienteSegmentado,
  ReglaAsociacion,
  VentaMensual,
  PedidoPorEstado,
  KpiProvincia,
} from '../models/dashboard.model';

@Injectable({
  providedIn: 'root',
})
export class AdminDashboardService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // =====================================================
  // DASHBOARD
  // =====================================================
  obtenerDashboardCompleto(): Observable<DashboardCompleto> {
    return forkJoin({
      resumen: this.http.get<AnaliticaResumen>(
        `${this.apiUrl}/analitica/dashboard/`,
        {
          withCredentials: true,
        },
      ),

      productos: this.http.get<ProductoMasVendido[]>(
        `${this.apiUrl}/analitica/productos-mas-vendidos-agrupados/`,
        {
          withCredentials: true,
        },
      ),

      categorias: this.http.get<CategoriaMasMovida[]>(
        `${this.apiUrl}/analitica/categorias-mas-movidas/`,
        {
          withCredentials: true,
        },
      ),

      clientes: this.http.get<ClienteSegmentado[]>(
        `${this.apiUrl}/analitica/clientes-segmentados/`,
        {
          withCredentials: true,
        },
      ),

      reglasResponse: this.http.get<any>(
        `${this.apiUrl}/analitica/reglas-asociacion/`,
        {
          withCredentials: true,
        },
      ),

      pedidosPorEstado: this.http.get<PedidoPorEstado[]>(
        `${this.apiUrl}/pedidos/admin/por-estado/`,
        {
          withCredentials: true,
        },
      ),

      ventasMensuales: this.http.get<VentaMensual[]>(
        `${this.apiUrl}/analitica/demanda-mensual/`,
        {
          withCredentials: true,
        },
      ),

      kpis: this.http.get<any>(
        `${this.apiUrl}/reporting/dashboard/`,
        {
          withCredentials: true,
        },
      ),

      ventasIngresosMensuales: this.http.get<
        { mes: number; total_ingresos: number }[]
      >(
        `${this.apiUrl}/analitica/ventas-mensuales/`,
        {
          withCredentials: true,
        },
      ),

      // =====================================================
      // KPIs POR PROVINCIA
      // =====================================================
      kpisProvincia: this.http.get<KpiProvincia[]>(
        `${this.apiUrl}/analitica/kpis-provincia/`,
        {
          withCredentials: true,
        },
      ),
    }).pipe(
      map((res: any) => ({
        resumen: res.resumen,
        productos: res.productos,
        categorias: res.categorias,
        clientes: res.clientes,
        reglas: res.reglasResponse.results || [],
        pedidosPorEstado: res.pedidosPorEstado || [],
        ventasMensuales: res.ventasMensuales,
        kpis: res.kpis,
        ventasIngresosMensuales: res.ventasIngresosMensuales || [],
        kpisProvincia: res.kpisProvincia || [],
      })),
    );
  }
}