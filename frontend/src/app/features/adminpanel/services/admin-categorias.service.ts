import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { CategoriaAdmin } from '../models/categoria-admin.model';

export interface CategoriasResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CategoriaAdmin[];
}

@Injectable({
  providedIn: 'root'
})
export class AdminCategoriasService {

  private apiUrl = `${environment.apiUrl}/productos/categorias`;

  constructor(private http: HttpClient) {}

  private getCsrfToken(): Observable<any> {
    return this.http.get(
      `${environment.apiUrl}/auth/csrf/`,
      {
        withCredentials: true
      }
    );
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
      switchMap(() =>
        this.http.post<CategoriaAdmin>(
          `${this.apiUrl}/`,
          data,
          {
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
      switchMap(() =>
        this.http.put<CategoriaAdmin>(
          `${this.apiUrl}/${id}/`,
          data,
          {
            withCredentials: true
          }
        )
      )
    );

  }

  eliminarCategoria(id: number): Observable<any> {

    return this.getCsrfToken().pipe(
      switchMap(() =>
        this.http.delete(
          `${this.apiUrl}/${id}/`,
          {
            withCredentials: true
          }
        )
      )
    );

  }

}