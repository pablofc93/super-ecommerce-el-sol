import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoApi } from '../models/producto-api.model';
import { PaginaApi } from '../models/pagina-api.model';
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
   * Obtiene una página de productos para las vistas de carga progresiva.
   */
  getProductosPagina(
    page: number,
    categoria?: number,
    pageSize: number = 12
  ): Observable<PaginaApi<Producto>> {
    let params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize);

    if (categoria !== undefined && categoria !== null) {
      params = params.set('categoria', categoria);
    }

    return this.http.get<PaginaApi<ProductoApi>>(this.apiUrl, {
      params,
      withCredentials: true,
    }).pipe(
      map((response) => ({
        ...response,
        results: ProductoAdapter.fromApiList(response.results),
      }))
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
