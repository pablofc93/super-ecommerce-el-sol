import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../../environments/environment';

/**decorador que permite que el servicio sea administrado por Angular
 * como servicio inyectable en toda la aplicación
 */
@Injectable({
  providedIn: 'root',
})
export class CarritoService {
  /** URL para las operaciones del carrito, utilizan este endpoint (/pedidos) */
  private apiUrl = `${environment.apiUrl}/pedidos`;

  private carritoSubject = new BehaviorSubject<any>(null); //mantiene el estado actual del carrito
  carrito$ = this.carritoSubject.asObservable(); //esta propiedad permite exponer el estado del carrito. Otros componentes pueden observar el cambio en el carrito

  constructor(private http: HttpClient) {}

  // =====================================
  // OBTENER CARRITO
  // =====================================
  obtenerCarrito(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/carrito/`, { withCredentials: true }) //withCredentials: true permite enviar las cookies de sesion asociadas al usuario
      .pipe(
        tap((carrito) => { //cuando el backend devuelve el carrito, tap actualiza su estado
          console.log('Carrito obtenido:', carrito);
          this.carritoSubject.next(carrito); //el carrito obtenido se almacena en carritoSubject, lo que permite que otros componentes puedan acceder a él
        }),
        catchError((error) => { //si ocurre un error, se almacena null en carritoSubject
          console.error('Error al obtener carrito:', error);
          this.carritoSubject.next(null);
          return of(null); //se devuelve of null, un observable para que la suscripción no se rompa y se pueda manejar el error de manera adecuada
        }),
      );
  }
  
  /**en el componente CarritoComponent se utiliza este método para obtener y cargar el carrito */
  getCarrito(): Observable<any> {
    return this.obtenerCarrito();
  }

  // =====================================
  // AGREGAR PRODUCTO - permite agregar productos al carrito
  // =====================================

  agregarProducto(productoId: number, cantidad: number = 1): Observable<any> {
    return this.http
      .post(
        `${this.apiUrl}/carrito/agregar/`,
        {
          producto_id: productoId,
          cantidad: cantidad,
        },
        { withCredentials: true },
      )
      .pipe(
        tap(() => {
          this.obtenerCarrito().subscribe(); //luego de actualizar el carrito, se vuelve a obtener el carrito actualizado para reflejar los cambios en la interfaz del usuario
        }),
        catchError((error) => {
          console.error('Error al agregar producto:', error);
          return of(null);
        }),
      );
  }

  // =====================================
  // ELIMINAR ITEM
  // =====================================

  eliminarItem(itemId: number): Observable<any> {
    return this.http
      .delete(`${this.apiUrl}/carrito/eliminar/item/${itemId}/`, {
        withCredentials: true,
      })
      .pipe(
        tap(() => {
          this.obtenerCarrito().subscribe(); //luego de eliminar el item del carrito carrito, se solicita nuevamente el carrito actualizado para reflejar los cambios en la interfaz del usuario
        }),
        catchError((error) => {
          console.error('Error al eliminar item:', error);
          return of(null);
        }),
      );
  }

  // =====================================
  // VACIAR CARRITO
  // =====================================

  vaciarCarrito(): Observable<any> {
    return this.http
      .delete(`${this.apiUrl}/carrito/vaciar/`, { withCredentials: true })
      .pipe(
        tap(() => {
          this.carritoSubject.next(null);
        }),
        catchError((error) => {
          console.error('Error al vaciar carrito:', error);
          return of(null);
        }),
      );
  }

  // =====================================
  // CONFIRMAR PEDIDO
  // =====================================

  confirmarPedido(montoPagado?: number): Observable<any> {
    return this.http
      .post(
        `${this.apiUrl}/confirmar/`,
        {
          monto_pagado: montoPagado ?? 0,
        },
        { withCredentials: true },
      )
      .pipe(
        tap(() => {
          console.log('Carrito vaciado correctamente');
        }),
        catchError((error) => {
          console.error('Error al confirmar pedido:', error);
          return of(null);
        }),
      );
  }

  // =====================================
  // UTILIDADES
  // =====================================

  calcularTotal(carrito: any): number {
    /**si el carrito no existe o existe pero no tiene items, el método termina
     * inmediatamente devolviendo 0
     */
    if (!carrito || !carrito.items) return 0;
    
    /**
     * el primer return devuelve el resultado de reduce
     * el return interno de reduce actualiza el acumulador de cada elemento
     */
    return carrito.items.reduce((total: number, item: any) => {
      return total + item.cantidad * item.precio_unitario;
    }, 0);
  }
  
  /** Este método obtiene la cantidad total de productos en el carrito */
  obtenerCantidadTotal(carrito: any): number {
    if (!carrito || !carrito.items) return 0;

    return carrito.items.reduce((total: number, item: any) => {
      return total + item.cantidad;
    }, 0);
  }
  
  /** Obtener el carrito actual desde el BeaviorSubject, lo que permite 
   * acceder al estado actual del carrito 
   * sin necesidad de suscribirse a un obserbavle */
  getCarritoActual(): any {
    return this.carritoSubject.value;
  }

  // =====================================
  // LIMPIAR ESTADO LOCAL
  // =====================================
  /**se utiliza para vaciar el carrito en el estado local */
  limpiarCarritoLocal(): void {
    this.carritoSubject.next(null);
  }
}