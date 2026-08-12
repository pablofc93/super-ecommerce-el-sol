import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Categoria } from '../models/categoria.model';

@Injectable({
  providedIn: 'root'
})
export class CategoriasService {

  private apiUrl = `${environment.apiUrl}/productos/categorias/`;

  constructor(private http: HttpClient) {}

  listar(): Observable<Categoria[]> {

    return this.http.get<any>(`${this.apiUrl}?all=true`).pipe(

      map((resp) => {

        if (Array.isArray(resp)) {
          return resp;
        }

        if (Array.isArray(resp.results)) {
          return resp.results;
        }

        console.warn('Respuesta inesperada categorias:', resp);
        return [];

      })

    );

  }

}