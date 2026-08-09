import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AdminReportingService {

  // ✅ usar backend correcto
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // =========================
  // PRODUCTOS
  // =========================

  getProductosMasVendidos(
    page: number = 1
  ): Observable<any> {

    return this.http.get<any>(
      `${this.baseUrl}/analitica/productos-mas-vendidos/?page=${page}`
    );

  }

  getProductosMasVendidosAgrupados(
    fechaInicio?: string,
    fechaFin?: string,
  ): Observable<any[]> {

    let params: any = {};

    if (fechaInicio) {
      params.fecha_inicio = fechaInicio;
    }

    if (fechaFin) {
      params.fecha_fin = fechaFin;
    }

    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/productos-mas-vendidos-agrupados/`,
      { params }
    );

  }

  getCategoriasMasMovidas(): Observable<any[]> {

    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/categorias-mas-movidas/`
    );

  }

  // =========================
  // CLIENTES
  // =========================

  getIngresosPorCliente(
    page: number = 1
  ): Observable<any> {

    return this.http.get<any>(
      `${this.baseUrl}/reporting/ingresos-clientes/?page=${page}`
    );

  }

  getClientesSegmentados(): Observable<any[]> {

    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/clientes-segmentados/`
    );

  }

  // =========================
  // RECOMENDACIONES
  // =========================

  getReglasAsociacion(
    page: number = 1
  ): Observable<any> {

    return this.http.get<any>(
      `${this.baseUrl}/analitica/reglas-asociacion/?page=${page}`
    );

  }

  // =========================
  // HISTÓRICOS
  // =========================

  getReportesHistoricos(
    page: number = 1
  ): Observable<any> {

    return this.http.get<any>(
      `${this.baseUrl}/reporting/historicos/?page=${page}`
    );

  }

  // =========================
  // REGISTRAR ACCESO
  // =========================

  registrarAcceso(tipo: string): Observable<any> {

    return this.http.post(
      `${this.baseUrl}/reporting/registrar-acceso/`,
      { tipo }
    );

  }

}