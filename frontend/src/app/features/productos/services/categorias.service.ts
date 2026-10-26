import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { Categoria } from '../models/categoria.model';
import { CategoriaApi } from '../models/categoria-api.model';
import { PaginaApi } from '../models/pagina-api.model';

@Injectable({
  providedIn: 'root'
})
export class CategoriasService {

  private apiUrl = `${environment.apiUrl}/productos/categorias/`;
  constructor(private http: HttpClient) {}

  /** el método listar realiza una solicitud GET y devuelve una lista de categorias */
  listar(): Observable<Categoria[]> {
    return this.http.get<any>(`${this.apiUrl}?all=true`).pipe( // all = true permite solicitar todas las cagorías disponibles
      
      /**se transforma y normaliza la respuesta
       * verifica si la respuesta es un array o si contiene una propiedad "results" que es un array
       * es decir, espera qu la respuesta tenga el formato esperado, y si no es así
       * devuelve un array vacío y muestra una advertencia en la consola
       */
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

  listarPagina(page: number, pageSize: number): Observable<PaginaApi<Categoria>> {
    const params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize);

    return this.http.get<PaginaApi<CategoriaApi>>(this.apiUrl, { params }).pipe(
      map((response) => ({
        ...response,
        results: response.results.map(({ id, nombre }) => ({ id, nombre })),
      }))
    );
  }

}