import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { CategoriaAdmin } from '../models/categoria-admin.model';

export interface CategoriasResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CategoriaAdmin[];
}

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root'
})
export class AdminCategoriasService {

  private apiUrl = `${environment.apiUrl}/productos/categorias`;

  constructor(private http: HttpClient) {}

  private getCsrfToken(): Observable<string> {
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

  private csrfHeaders(token: string): HttpHeaders {
    return new HttpHeaders({ 'X-CSRFToken': token });
  }

  listarCategorias(
    page: number = 1,
    search: string = ''
  ): Observable<CategoriasResponse> {

    let params = new HttpParams()
      .set('page', page);

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<CategoriasResponse>(
      `${this.apiUrl}/`,
      {
        params,
        withCredentials: true
      }
    );
  }

  crearCategoria(data: {
    nombre: string;
    descripcion: string;
  }): Observable<CategoriaAdmin> {

    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.post<CategoriaAdmin>(
          `${this.apiUrl}/`,
          data,
          {
            headers: this.csrfHeaders(token),
            withCredentials: true
          }
        )
      )
    );

  }

  actualizarCategoria(
    id: number,
    data: CategoriaAdmin
  ): Observable<CategoriaAdmin> {

    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.put<CategoriaAdmin>(
          `${this.apiUrl}/${id}/`,
          data,
          {
            headers: this.csrfHeaders(token),
            withCredentials: true
          }
        )
      )
    );

  }

  eliminarCategoria(id: number): Observable<any> {

    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.delete(
          `${this.apiUrl}/${id}/`,
          {
            headers: this.csrfHeaders(token),
            withCredentials: true
          }
        )
      )
    );

  }

}