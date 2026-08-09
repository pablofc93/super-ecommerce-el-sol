import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Pedido, PaginatedResponse } from '../models/pedido.model';

@Injectable({
  providedIn: 'root',
})
export class PedidoService {
  private apiUrl = `${environment.apiUrl}/pedidos`;

  constructor(private http: HttpClient) {}

  // =====================================
  // LISTAR PEDIDOS (CON PAGINACIÓN)
  // =====================================

  listarPedidos(page: number = 1): Observable<PaginatedResponse<Pedido>> {
    return this.http
      .get<
        PaginatedResponse<Pedido>
      >(`${this.apiUrl}/listar/?page=${page}`, { withCredentials: true })
      .pipe(
        catchError((error) => {
          console.error('Error al listar pedidos:', error);
          return of({
            count: 0,
            next: null,
            previous: null,
            results: [],
          });
        }),
      );
  }

  // =====================================
  // CANCELAR PEDIDO
  // =====================================

  cancelarPedido(pedidoId: number): Observable<any> {
    return this.http
      .post(
        `${this.apiUrl}/cancelar/${pedidoId}/`,
        {},
        { withCredentials: true },
      )
      .pipe(
        catchError((error) => {
          console.error('Error al cancelar pedido:', error);
          return of(null);
        }),
      );
  }
}
