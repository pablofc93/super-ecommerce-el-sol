import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class CarritoService {
  private apiUrl = `${environment.apiUrl}/pedidos`;

  private carritoSubject = new BehaviorSubject<any>(null);
  carrito$ = this.carritoSubject.asObservable();

  constructor(private http: HttpClient) {}

  // =====================================
  // OBTENER CARRITO
  // =====================================

  obtenerCarrito(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/carrito/`, { withCredentials: true })
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

  getCarrito(): Observable<any> {
    return this.obtenerCarrito();
  }

  // =====================================
  // AGREGAR PRODUCTO
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
    return this.http
      .delete(`${this.apiUrl}/carrito/eliminar/item/${itemId}/`, {
        withCredentials: true,
      })
      .pipe(
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
    if (!carrito || !carrito.items) return 0;

    return carrito.items.reduce((total: number, item: any) => {
      return total + item.cantidad * item.precio_unitario;
    }, 0);
  }

  obtenerCantidadTotal(carrito: any): number {
    if (!carrito || !carrito.items) return 0;

    return carrito.items.reduce((total: number, item: any) => {
      return total + item.cantidad;
    }, 0);
  }

  getCarritoActual(): any {
    return this.carritoSubject.value;
  }

  // =====================================
  // LIMPIAR ESTADO LOCAL
  // =====================================

  limpiarCarritoLocal(): void {
    this.carritoSubject.next(null);
  }
}