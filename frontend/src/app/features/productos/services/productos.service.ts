import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, expand, map, reduce } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoApi } from '../models/producto-api.model';
import { Producto } from '../models/producto.model';
import { ProductoAdapter } from '../adapters/producto.adapter';

@Injectable({
  providedIn: 'root',
})
export class ProductosService {

  private apiUrl = `${environment.apiUrl}/productos/productos/`;
  private analiticaUrl = `${environment.apiUrl}/analitica/`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene los productos.
   * Si se envía una categoría, el filtrado se realiza
   * directamente en el backend.
   */
  getProductos(categoria?: number): Observable<Producto[]> {

    let url = this.apiUrl;

    if (categoria !== undefined && categoria !== null) {
      url += `?categoria=${categoria}`;
    }

    return this.http.get<any>(url).pipe(

      expand(response =>
        response.next
          ? this.http.get<any>(response.next)
          : []
      ),

      reduce((acumulado, response) => {

        const productosPagina = response.results ?? response;

        return [...acumulado, ...productosPagina];

      }, [] as ProductoApi[]),

      map(productos =>
        ProductoAdapter.fromApiList(productos)
      )

    );

  }

  /**
   * Obtiene un producto por ID
   */
  getProductoById(id: number): Observable<Producto> {

    return this.http
      .get<ProductoApi>(`${this.apiUrl}${id}/`)
      .pipe(
        map(prod => ProductoAdapter.fromApi(prod))
      );

  }

  /**
   * Obtiene los productos más vendidos para mostrar
   * en la pantalla de inicio del cliente.
   */
  getProductosMasVendidos(): Observable<Producto[]> {

    return this.http
      .get<ProductoApi[]>(
        `${this.analiticaUrl}productos-mas-vendidos-public/`
      )
      .pipe(
        map(productos => ProductoAdapter.fromApiList(productos))
      );

  }

}