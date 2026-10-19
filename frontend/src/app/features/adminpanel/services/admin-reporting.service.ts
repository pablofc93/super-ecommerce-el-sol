import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';

import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AdminReportingService {

  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // =========================
  // TOKEN CSRF
  // =========================

  /**
   * Obtiene un token CSRF desde Django.
   * El endpoint debe devolver { csrfToken: string }.
   */
  private obtenerTokenCsrf(): Observable<string> {
    return this.http
      .get<{ csrfToken: string }>(
        `${this.baseUrl}/csrf/`,
        { withCredentials: true }
      )
      .pipe(
        map((respuesta) => respuesta.csrfToken)
      );
  }

  // =========================
  // PRODUCTOS
  // =========================

  getProductosMasVendidos(
    page: number = 1
  ): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/analitica/productos-mas-vendidos/?page=${page}`,
      { withCredentials: true }
    );
  }

  getProductosMasVendidosAgrupados(
    fechaInicio?: string,
    fechaFin?: string,
  ): Observable<any[]> {
    const params: any = {};

    if (fechaInicio) {
      params.fecha_inicio = fechaInicio;
    }

    if (fechaFin) {
      params.fecha_fin = fechaFin;
    }

    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/productos-mas-vendidos-agrupados/`,
      {
        params,
        withCredentials: true
      }
    );
  }

  getCategoriasMasMovidas(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/categorias-mas-movidas/`,
      { withCredentials: true }
    );
  }

  // =========================
  // CLIENTES
  // =========================

  getIngresosPorCliente(
    page: number = 1
  ): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/reporting/ingresos-clientes/?page=${page}`,
      { withCredentials: true }
    );
  }

  getClientesSegmentados(): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/analitica/clientes-segmentados/`,
      { withCredentials: true }
    );
  }

  // =========================
  // RECOMENDACIONES
  // =========================

  getReglasAsociacion(
    page: number = 1
  ): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/analitica/reglas-asociacion/?page=${page}`,
      { withCredentials: true }
    );
  }

  // =========================
  // HISTÓRICOS
  // =========================

  getReportesHistoricos(
    page: number = 1
  ): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/reporting/historicos/?page=${page}`,
      { withCredentials: true }
    );
  }

  // =========================
  // REGISTRAR ACCESO
  // =========================

  registrarAcceso(tipo: string): Observable<any> {
    return this.obtenerTokenCsrf().pipe(
      switchMap((csrfToken) =>
        this.http.post(
          `${this.baseUrl}/reporting/registrar-acceso/`,
          { tipo },
          {
            withCredentials: true,
            headers: new HttpHeaders({
              'X-CSRFToken': csrfToken
            })
          }
        )
      )
    );
  }
}