import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';

import { PedidoAdmin } from '../models/pedido-admin.model';
import { PedidoEstado } from '../../../shared/enums/pedido-estado.enum';
import { PedidoDetalle } from '../../../shared/models/pedido-detalle.model';

import { environment } from '../../../../environments/environment';

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root',
})
export class AdminPedidosService {
  private http = inject(HttpClient);

  private apiUrl = `${environment.apiUrl}/pedidos`;

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

  listarPedidos(
    page: number = 1,
    search: string = '',
  ): Observable<any> {
  
    return this.http.get<any>(
      `${this.apiUrl}/admin/listar/?page=${page}&search=${encodeURIComponent(search)}`
    );
  
  }

  cambiarEstado(pedidoId: number, estado: PedidoEstado): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.patch(
          `${this.apiUrl}/admin/${pedidoId}/estado/`,
          { estado },
          {
            headers: new HttpHeaders({ 'X-CSRFToken': token }),
            withCredentials: true,
          }
        )
      )
    );
  }

  detallePedido(pedidoId: number): Observable<PedidoDetalle> {
    return this.http.get<PedidoDetalle>(`${this.apiUrl}/admin/${pedidoId}/`);
  }
}
