import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoApi } from '../../productos/models/producto-api.model';
import { Producto } from '../../productos/models/producto.model';
import { ProductoAdapter } from '../../productos/adapters/producto.adapter';

@Injectable({
  providedIn: 'root',
})
export class RecomendacionService {
  private readonly apiUrl = `${environment.apiUrl}/recomendacion/cliente/`;

  constructor(private http: HttpClient) {}

  obtenerPorCliente(clienteId: number): Observable<Producto[]> {
    return this.http
      .get<ProductoApi[]>(`${this.apiUrl}${clienteId}/`, {
        withCredentials: true,
      })
      .pipe(map((productos) => ProductoAdapter.fromApiList(productos)));
  }
}
