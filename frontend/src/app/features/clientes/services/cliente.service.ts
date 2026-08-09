import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

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

@Injectable({
  providedIn: 'root'
})
export class ClienteService {

  private apiUrl = `${environment.apiUrl}/clientes`;

  constructor(private http: HttpClient) {}

  getPerfil(): Observable<ClientePerfil> {

    return this.http.get<ClientePerfil>(
      `${this.apiUrl}/me/`,
      { withCredentials: true }
    );

  }

  updatePerfil(data: Partial<ClientePerfil>): Observable<ClientePerfil> {

    return this.http.patch<ClientePerfil>(
      `${this.apiUrl}/me/`,
      data,
      { withCredentials: true }
    );

  }
}