import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { UsuarioAdmin } from '../models/usuario-admin.model';

export interface UsuariosResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: UsuarioAdmin[];
}

@Injectable({
  providedIn: 'root'
})
export class AdminUsuariosService {

  private apiUrl = `${environment.apiUrl}/auth/admin`;

  constructor(private http: HttpClient) {}

  private getCsrfToken(): Observable<any> {
    return this.http.get(
      `${environment.apiUrl}/auth/csrf/`,
      { withCredentials: true }
    );
  }

  listarUsuarios(page: number = 1, search: string = ''): Observable<UsuariosResponse> {

    let params = new HttpParams()
      .set('page', page);

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<UsuariosResponse>(
      `${this.apiUrl}/listar/`,
      { params, withCredentials: true }
    );
  }

  crearUsuario(data: {
    username: string;
    email: string;
    password: string;
    tipo_usuario: 'admin' | 'cliente';
  }): Observable<UsuarioAdmin> {
    return this.getCsrfToken().pipe(
      switchMap(() =>
        this.http.post<UsuarioAdmin>(
          `${this.apiUrl}/crear/`,
          data,
          { withCredentials: true }
        )
      )
    );
  }

  cambiarRol(userId: number, tipo_usuario: 'admin' | 'cliente'): Observable<any> {
    return this.getCsrfToken().pipe(
      switchMap(() =>
        this.http.patch(
          `${this.apiUrl}/${userId}/rol/`,
          { tipo_usuario },
          { withCredentials: true }
        )
      )
    );
  }

  eliminarUsuario(userId: number): Observable<any> {
    return this.getCsrfToken().pipe(
      switchMap(() =>
        this.http.delete(
          `${this.apiUrl}/${userId}/eliminar/`,
          { withCredentials: true }
        )
      )
    );
  }
}