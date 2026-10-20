import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, map, of, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Pedido, PaginatedResponse } from '../models/pedido.model';

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({ providedIn: 'root' })
export class PedidoService {

  /** URL base para las solicitudes a la API de pedidos */
  private apiUrl = `${environment.apiUrl}/pedidos`;

  constructor(private http: HttpClient) {}

  private obtenerCsrfToken(): Observable<string> {
    return this.http
      .get<CsrfResponse>(`${environment.apiUrl}/csrf/`, {
        withCredentials: true
      })
      .pipe(
        map(({ csrfToken }) => {
          if (!csrfToken) {
            throw new Error('El backend no devolvió el token CSRF.');
          }

          return csrfToken;
        })
      );
  }

  // LISTAR PEDIDOS (CON PAGINACIÓN)
  listarPedidos(page: number = 1): Observable<PaginatedResponse<Pedido>> {
    return this.http.get<PaginatedResponse<Pedido>>(`${this.apiUrl}/listar/?page=${page}`, { withCredentials: true }).pipe(
      catchError((error) => {
        console.error('Error al listar pedidos:', error);
        return of({ count: 0, next: null, previous: null, results: [] });
      }),
    );
  }
  
  // CANCELAR PEDIDO
  cancelarPedido(pedidoId: number): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.post(
          `${this.apiUrl}/cancelar/${pedidoId}/`,
          {},
          {
            headers: new HttpHeaders({ 'X-CSRFToken': token }),
            withCredentials: true
          }
        )
      ),
    ).pipe(
      catchError((error) => {
        console.error('Error al cancelar pedido:', error);
        return of(null);
      }),
    );
  }
}