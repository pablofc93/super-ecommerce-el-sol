import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map, switchMap } from 'rxjs';
import { environment } from '../../../../environments/environment';

/*aqui se define la interfaz del cliente
Esta interfaz representa la estructura de los datos utilizados
por el perfil del cliente*/
export interface ClientePerfil {

  username: string;
  email: string;

  first_name?: string;
  last_name?: string;
  
  telefono?: string;

  direccion?: string;
  ciudad?: string;
  provincia?: string;
  codigo_postal?: string;

  password?: string;

}

interface CsrfResponse {
  csrfToken: string;
}

@Injectable({
  providedIn: 'root'
})
export class ClienteService {

  private apiUrl = `${environment.apiUrl}/clientes`;

  constructor(private http: HttpClient) {}

  private obtenerCsrfToken(): Observable<string> {
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
  
  /**este método se encarga de obtener los datos del perfil del cliente
   * desde el backend
   */

  /**OBTENER EL PERFIL */
  getPerfil(): Observable<ClientePerfil> {

    return this.http.get<ClientePerfil>(
      `${this.apiUrl}/me/`,
      { withCredentials: true }
    );

  }
  
  /**ACTUALIZAR EL PERFIL */
  updatePerfil(data: Partial<ClientePerfil>): Observable<ClientePerfil> {
    return this.obtenerCsrfToken().pipe(
      switchMap((token) =>
        this.http.patch<ClientePerfil>(
          `${this.apiUrl}/me/`,
          data,
          {
            headers: new HttpHeaders({ 'X-CSRFToken': token }),
            withCredentials: true
          }
        )
      )
    );
  }
}