
import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpHeaders,
  HttpParams,
} from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoAdmin } from '../models/producto-admin.model';

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root',
})
export class AdminProductosService {
  private readonly apiUrl =
    `${environment.apiUrl}/productos/productos/`;

  private readonly csrfUrl =
    `${environment.apiUrl}/csrf/`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene un token CSRF válido desde Django.
   * La respuesta también permite que Django establezca
   * la cookie csrftoken en el dominio del backend.
   */
  private obtenerCsrfToken(): Observable<string> {
    return this.http
      .get<CsrfResponse>(this.csrfUrl, {
        withCredentials: true,
      })
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
   * Construye los encabezados para operaciones protegidas.
   */
  private crearHeadersCsrf(token: string): HttpHeaders {
    return new HttpHeaders({
      'X-CSRFToken': token,
    });
  }

  /**
   * Lista productos con paginación y búsqueda.
   */
  listar(
    page: number = 1,
    search: string = ''
  ): Observable<any> {
    let params = new HttpParams().set(
      'page',
      page.toString()
    );

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<any>(this.apiUrl, {
      params,
      withCredentials: true,
    });
  }

  /**
   * Crea un producto.
   */
  crear(data: FormData): Observable<ProductoAdmin> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.post<ProductoAdmin>(
          this.apiUrl,
          data,
          {
            headers: this.crearHeadersCsrf(token),
            withCredentials: true,
          }
        )
      )
    );
  }

  /**
   * Actualiza un producto existente.
   */
  actualizar(
    id: number,
    data: FormData
  ): Observable<ProductoAdmin> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.put<ProductoAdmin>(
          `${this.apiUrl}${id}/`,
          data,
          {
            headers: this.crearHeadersCsrf(token),
            withCredentials: true,
          }
        )
      )
    );
  }

  /**
   * Elimina un producto.
   */
  eliminar(id: number): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.delete(
          `${this.apiUrl}${id}/`,
          {
            headers: this.crearHeadersCsrf(token),
            withCredentials: true,
          }
        )
      )
    );
  }
}
