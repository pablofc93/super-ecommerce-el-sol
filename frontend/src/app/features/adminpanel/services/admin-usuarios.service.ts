import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpHeaders,
  HttpParams,
} from '@angular/common/http';

import { Observable, switchMap } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { UsuarioAdmin } from '../models/usuario-admin.model';

export interface UsuariosResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: UsuarioAdmin[];
}

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root',
})
export class AdminUsuariosService {
  private apiUrl = `${environment.apiUrl}/auth/admin`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene un token CSRF válido desde Django.
   * El endpoint también establece la cookie CSRF.
   */
  private obtenerCsrfToken(): Observable<string> {
    return this.http
      .get<CsrfResponse>(
        `${environment.apiUrl}/csrf/`,
        { withCredentials: true }
      )
      .pipe(
        switchMap((respuesta) => {
          if (!respuesta?.csrfToken) {
            throw new Error(
              'Django no devolvió el token CSRF esperado.'
            );
          }

          // Emitimos el token para utilizarlo en la petición siguiente.
          return new Observable<string>((subscriber) => {
            subscriber.next(respuesta.csrfToken);
            subscriber.complete();
          });
        })
      );
  }

  /**
   * Construye los encabezados necesarios para Django.
   */
  private crearHeadersCsrf(token: string): HttpHeaders {
    return new HttpHeaders({
      'X-CSRFToken': token,
    });
  }

  /**
   * Lista los usuarios registrados.
   */
  listarUsuarios(
    page: number = 1,
    search: string = ''
  ): Observable<UsuariosResponse> {
    let params = new HttpParams().set('page', page);

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<UsuariosResponse>(
      `${this.apiUrl}/listar/`,
      {
        params,
        withCredentials: true,
      }
    );
  }

  /**
   * Crea un usuario desde el panel administrativo.
   */
  crearUsuario(data: {
    username: string;
    email: string;
    password: string;
    tipo_usuario: 'admin' | 'cliente';
  }): Observable<UsuarioAdmin> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.post<UsuarioAdmin>(
          `${this.apiUrl}/crear/`,
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
   * Cambia el rol de un usuario.
   */
  cambiarRol(
    userId: number,
    tipo_usuario: 'admin' | 'cliente'
  ): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.patch(
          `${this.apiUrl}/${userId}/rol/`,
          { tipo_usuario },
          {
            headers: this.crearHeadersCsrf(token),
            withCredentials: true,
          }
        )
      )
    );
  }

  /**
   * Elimina un usuario.
   */
  eliminarUsuario(userId: number): Observable<any> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.delete(
          `${this.apiUrl}/${userId}/eliminar/`,
          {
            headers: this.crearHeadersCsrf(token),
            withCredentials: true,
          }
        )
      )
    );
  }
}