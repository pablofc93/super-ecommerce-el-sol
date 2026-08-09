import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoAdmin } from '../models/producto-admin.model';

@Injectable({
  providedIn: 'root'
})
export class AdminProductosService {

  // ✅ URL CORRECTA
  private apiUrl = `${environment.apiUrl}/productos/productos/`;

  constructor(private http: HttpClient) {}

  listar(page: number = 1, search: string = ''): Observable<any> {

    let params = new HttpParams()
      .set('page', page.toString());

    if (search) {
      params = params.set('search', search);
    }

    return this.http.get<any>(this.apiUrl, { params });

  }

  crear(data: FormData): Observable<ProductoAdmin> {
    return this.http.post<ProductoAdmin>(this.apiUrl, data);
  }

  actualizar(id: number, data: FormData): Observable<ProductoAdmin> {
    return this.http.put<ProductoAdmin>(
      `${this.apiUrl}${id}/`,
      data
    );
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}${id}/`
    );
  }
}