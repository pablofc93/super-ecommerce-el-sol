import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  BehaviorSubject,
  Observable,
  tap,
  catchError,
  of,
  map,
  switchMap,
} from 'rxjs';
import { environment } from '../../../../environments/environment';

/** Servicio encargado de gestionar el carrito de compras. */
@Injectable({
  providedIn: 'root',
})
export class CarritoService {
  /** URL base para las operaciones de pedidos. */
  private apiUrl = `${environment.apiUrl}/pedidos`;

  /** Estado actual del carrito. */
  private carritoSubject = new BehaviorSubject<any>(null);
  carrito$ = this.carritoSubject.asObservable();

  constructor(private http: HttpClient) {}

  // =====================================
  // OBTENER TOKEN CSRF
  // =====================================

  /**
   * Solicita a Django un token CSRF.
   * Requiere que exista el endpoint /api/csrf/
   * en el backend.
   */
  private obtenerTokenCsrf(): Observable<string> {
    return this.http
      .get<{
        csrfToken: string;
      }>(`${environment.apiUrl}/csrf/`, { withCredentials: true })
      .pipe(map((respuesta) => respuesta.csrfToken));
  }

  /**
   * Ejecuta una petición que modifica datos
   * incluyendo el encabezado CSRF requerido por Django.
   */
  private conTokenCsrf<T>(
    peticion: (headers: HttpHeaders) => Observable<T>,
  ): Observable<T> {
    return this.obtenerTokenCsrf().pipe(
      switchMap((csrfToken) =>
        peticion(
          new HttpHeaders({
            'X-CSRFToken': csrfToken,
          }),
        ),
      ),
    );
  }

  // =====================================
  // OBTENER CARRITO
  // =====================================

  obtenerCarrito(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/carrito/`, {
        withCredentials: true,
      })
      .pipe(
        tap((carrito) => {
          console.log('Carrito obtenido:', carrito);
          this.carritoSubject.next(carrito);
        }),
        catchError((error) => {
          console.error('Error al obtener carrito:', error);
          this.carritoSubject.next(null);
          return of(null);
        }),
      );
  }

  /** Obtiene el carrito para el componente correspondiente. */
  getCarrito(): Observable<any> {
    return this.obtenerCarrito();
  }

  // =====================================
  // AGREGAR PRODUCTO
  // =====================================

  agregarProducto(productoId: number, cantidad: number = 1): Observable<any> {
    return this.conTokenCsrf((headers) =>
      this.http.post(
        `${this.apiUrl}/carrito/agregar/`,
        {
          producto_id: productoId,
          cantidad: cantidad,
        },
        {
          withCredentials: true,
          headers,
        },
      ),
    ).pipe(
      tap(() => {
        this.obtenerCarrito().subscribe();
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
    return this.conTokenCsrf((headers) =>
      this.http.delete(`${this.apiUrl}/carrito/eliminar/item/${itemId}/`, {
        withCredentials: true,
        headers,
      }),
    ).pipe(
      tap(() => {
        this.obtenerCarrito().subscribe();
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
    return this.conTokenCsrf((headers) =>
      this.http.delete(`${this.apiUrl}/carrito/vaciar/`, {
        withCredentials: true,
        headers,
      }),
    ).pipe(
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
    return this.conTokenCsrf((headers) =>
      this.http.post(
        `${this.apiUrl}/confirmar/`,
        {
          monto_pagado: montoPagado ?? 0,
        },
        {
          withCredentials: true,
          headers,
        },
      ),
    ).pipe(
      tap(() => {
        console.log('Pedido confirmado correctamente');
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

  /** Calcula el importe total del carrito. */
  calcularTotal(carrito: any): number {
    if (!carrito || !carrito.items) return 0;

    return carrito.items.reduce(
      (total: number, item: any) =>
        total + item.cantidad * item.precio_unitario,
      0,
    );
  }

  /** Obtiene la cantidad total de productos del carrito. */
  obtenerCantidadTotal(carrito: any): number {
    if (!carrito || !carrito.items) return 0;

    return carrito.items.reduce(
      (total: number, item: any) => total + item.cantidad,
      0,
    );
  }

  /** Devuelve el carrito almacenado en el estado local. */
  getCarritoActual(): any {
    return this.carritoSubject.value;
  }

  // =====================================
  // LIMPIAR ESTADO LOCAL
  // =====================================

  /** Limpia el estado local del carrito. */
  limpiarCarritoLocal(): void {
    this.carritoSubject.next(null);
  }
}
