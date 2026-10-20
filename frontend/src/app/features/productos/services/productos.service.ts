import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  Observable,
  expand,
  map,
  reduce,
  switchMap,
} from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoApi } from '../models/producto-api.model';
import { Producto } from '../models/producto.model';
import { ProductoAdapter } from '../adapters/producto.adapter';

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root',
})
export class ProductosService {

  // URL principal para las operaciones de productos.
  private apiUrl = `${environment.apiUrl}/productos/productos/`;

  // URL para las consultas de analítica.
  private analiticaUrl = `${environment.apiUrl}/analitica/`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene un token CSRF desde Django.
   * Se envían las cookies para mantener la sesión.
   */
  private obtenerCsrfToken(): Observable<string> {
    return this.http
      .get<CsrfResponse>(
        `${environment.apiUrl}/csrf/`,
        { withCredentials: true }
      )
      .pipe(
        map((respuesta) => {
          if (!respuesta?.csrfToken) {
            throw new Error(
              'El backend no devolvió el token CSRF.'
            );
          }

          return respuesta.csrfToken;
        })
      );
  }

  /**
   * Crea un producto y envía los datos mediante FormData.
   * Permite incluir la imagen sin establecer manualmente
   * el encabezado Content-Type.
   */
  crearProducto(datos: FormData): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.post(
          this.apiUrl,
          datos,
          {
            headers: new HttpHeaders({
              'X-CSRFToken': token,
            }),
            withCredentials: true,
          }
        )
      )
    );
  }

  /**
   * Obtiene los productos, con filtrado opcional por categoría
   * y soporte para paginación.
   */
  getProductos(categoria?: number): Observable<Producto[]> {

    let url = this.apiUrl;

    if (categoria !== undefined && categoria !== null) {
      url += `?categoria=${categoria}`;
    }

    return this.http.get<any>(url, {
      withCredentials: true,
    }).pipe(
      expand((response) =>
        response.next
          ? this.http.get<any>(response.next, {
              withCredentials: true,
            })
          : []
      ),

      reduce((acumulado, response) => {
        const productosPagina = response.results ?? response;

        return [...acumulado, ...productosPagina];
      }, [] as ProductoApi[]),

      map((productos) =>
        ProductoAdapter.fromApiList(productos)
      )
    );
  }

  /**
   * Obtiene un producto por su ID.
   */
  getProductoById(id: number): Observable<Producto> {
    return this.http
      .get<ProductoApi>(`${this.apiUrl}${id}/`, {
        withCredentials: true,
      })
      .pipe(
        map((prod) => ProductoAdapter.fromApi(prod))
      );
  }

  /**
   * Obtiene los productos más vendidos.
   */
  getProductosMasVendidos(): Observable<Producto[]> {
    return this.http
      .get<ProductoApi[]>(
        `${this.analiticaUrl}productos-mas-vendidos-public/`,
        { withCredentials: true }
      )
      .pipe(
        map((productos) =>
          ProductoAdapter.fromApiList(productos)
        )
      );
  }
}
