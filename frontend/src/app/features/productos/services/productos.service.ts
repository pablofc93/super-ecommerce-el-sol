import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, expand, map, reduce } from 'rxjs';

import { environment } from '../../../../environments/environment';
import { ProductoApi } from '../models/producto-api.model';
import { Producto } from '../models/producto.model';
import { ProductoAdapter } from '../adapters/producto.adapter';

@Injectable({
  providedIn: 'root',
})
export class ProductosService {
  
  // el servicio utiliza 2 URLs principales: una para productos y otra para analítica
  private apiUrl = `${environment.apiUrl}/productos/productos/`;
  private analiticaUrl = `${environment.apiUrl}/analitica/`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene los productos.
   * Si se envía una categoría, el filtrado se realiza
   * directamente en el backend.
   */
  getProductos(categoria?: number): Observable<Producto[]> {
    
    // se inicializa la url
    let url = this.apiUrl;
    
    //se comprueba si se proporciona o no la categoría
    if (categoria !== undefined && categoria !== null) {
      url += `?categoria=${categoria}`; //se agrega la categoría como parámetro de consulta, el backend lo usa para filtrar los productos
    }

    return this.http.get<any>(url).pipe( //se realiza la petición HTTP
      
      // permite manejar la paginación de los resultados, 
      // si el backend devuelve una propiedad "next" 
      // con la URL de la siguiente página, se hace una 
      // petición HTTP a esa URL y se repite el proceso 
      // hasta que no haya más páginas
      expand(response =>
        response.next
          ? this.http.get<any>(response.next)
          : []
      ),
      
      // acumula los productos en un único array,
      // combinando los productos de todas las páginas
      reduce((acumulado, response) => {
        const productosPagina = response.results ?? response;
        return [...acumulado, ...productosPagina];
      }, [] as ProductoApi[]),
      
      // aquí se transforma la lista de productos del backend 
      // (ProductoApi) a la estructura utilizada por Angular (Producto)
      map(productos =>
        ProductoAdapter.fromApiList(productos)
      )

    );

  }

  /**
   * Obtiene un único producto por ID
   * la respuesta se recibe como ProductoApi y se transforma a 
   * Producto usando ProductoAdapter
   */
  getProductoById(id: number): Observable<Producto> {

    return this.http
      .get<ProductoApi>(`${this.apiUrl}${id}/`)
      .pipe(
        map(prod => ProductoAdapter.fromApi(prod))
      );

  }

  /**
   * Obtiene los productos más vendidos para mostrar
   * en la pantalla de inicio del cliente.
   * la respuesta se recibe como ProductoApi[] y se transforma a 
   *  Producto[] usando ProductoAdapter
   */
  getProductosMasVendidos(): Observable<Producto[]> {

    return this.http
      .get<ProductoApi[]>(
        `${this.analiticaUrl}productos-mas-vendidos-public/`
      )
      .pipe(
        map(productos => ProductoAdapter.fromApiList(productos))
      );

  }

}