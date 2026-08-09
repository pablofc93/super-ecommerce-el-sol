import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { PedidoAdmin } from '../models/pedido-admin.model';
import { PedidoEstado } from '../../../shared/enums/pedido-estado.enum';
import { PedidoDetalle } from '../../../shared/models/pedido-detalle.model';

import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AdminPedidosService {
  private http = inject(HttpClient);

  private apiUrl = `${environment.apiUrl}/pedidos`;

  listarPedidos(
    page: number = 1,
    search: string = '',
  ): Observable<any> {
  
    return this.http.get<any>(
      `${this.apiUrl}/admin/listar/?page=${page}&search=${encodeURIComponent(search)}`
    );
  
  }

  cambiarEstado(pedidoId: number, estado: PedidoEstado): Observable<any> {
    return this.http.patch(`${this.apiUrl}/admin/${pedidoId}/estado/`, {
      estado,
    });
  }

  detallePedido(pedidoId: number): Observable<PedidoDetalle> {
    return this.http.get<PedidoDetalle>(`${this.apiUrl}/admin/${pedidoId}/`);
  }
}
