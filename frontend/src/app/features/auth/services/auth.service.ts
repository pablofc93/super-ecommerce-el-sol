import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, catchError, of, switchMap, finalize } from 'rxjs';
import { Router } from '@angular/router';
import { User } from '../models/user.model';
import { environment } from '../../../../environments/environment';
import { CarritoService } from '../../pedidos/services/carrito.service';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private userSubject = new BehaviorSubject<User | null>(null);
  public user$ = this.userSubject.asObservable();
  private initializedSubject = new BehaviorSubject<boolean>(false);
  public initialized$ = this.initializedSubject.asObservable();
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(
    private http: HttpClient,
    private router: Router,
    private carritoService: CarritoService,
  ) {}

  private getCsrfToken(): Observable<any> {
    return this.http.get(`${this.apiUrl}/csrf/`, { withCredentials: true });
  }

  // =========================
  // REGISTER
  // =========================
  register(data: { username: string; first_name: string; last_name: string; email: string; password: string }): Observable<User> {
    return this.getCsrfToken().pipe(
      switchMap(() => this.http.post<User>(`${this.apiUrl}/register/`, data, { withCredentials: true })),
      switchMap(() => this.login(data.username, data.password)),
    );
  }

  // =========================
  // LOGIN
  // =========================
  login(username: string, password: string): Observable<User> {
    return this.getCsrfToken().pipe(
      switchMap(() => this.http.post<User>(`${this.apiUrl}/login/`, { username, password }, { withCredentials: true })),
      tap((user) => {
        // Guardar usuario autenticado
        this.userSubject.next(user);
        // Cargar carrito automáticamente
        // para clientes
        if (user.tipo_usuario === 'cliente' || user.tipo_usuario === 'usuario') {
          this.carritoService.obtenerCarrito().subscribe();
        }
      }),
    );
  }

  // =========================
  // LOGOUT
  // =========================
  logout() {
    return this.http.post(`${environment.apiUrl}/auth/logout/`, {}, { withCredentials: true }).pipe(
      catchError((error) => {
        if (error.status === 403) {
          console.warn('Sesión ya inválida');
        }
        return of(null);
      }),
      tap(() => {
        // limpiar usuario
        this.userSubject.next(null);
        // limpiar solamente memoria local
        // NO elimina carrito de BD
        this.carritoService.limpiarCarritoLocal();
        localStorage.clear();
      }),
    );
  }

  forceLogout() {
    this.userSubject.next(null);
    this.carritoService.limpiarCarritoLocal();
    this.router.navigate(['/login']);
  }

  // =========================
  // ME
  // =========================
  getMe(): Observable<User | null> {
    return this.http.get<User>(`${this.apiUrl}/me/`, { withCredentials: true }).pipe(
      tap((user) => {
        this.userSubject.next(user);
        // Recuperar carrito al refrescar página
        if (user.tipo_usuario === 'cliente' || user.tipo_usuario === 'usuario') {
          this.carritoService.obtenerCarrito().subscribe();
        }
      }),
      catchError(() => {
        this.userSubject.next(null);
        this.carritoService.limpiarCarritoLocal();
        return of(null);
      }),
    );
  }

  updateMe(data: {
    username?: string;
    email?: string;
    telefono?: string;
    direccion?: string;
    ciudad?: string;
    provincia?: string;
    codigo_postal?: string;
  }): Observable<User> {
    return this.getCsrfToken().pipe(
      switchMap(() => this.http.patch<User>(`${this.apiUrl}/me/`, data, { withCredentials: true })),
      tap((updatedUser) => this.userSubject.next(updatedUser)),
    );
  }

  initializeAuth(): void {
    this.getMe().pipe(finalize(() => this.initializedSubject.next(true))).subscribe();
  }

  isLoggedIn(): boolean {
    return this.userSubject.value !== null;
  }

  getCurrentUser(): User | null {
    return this.userSubject.value;
  }

  changePassword(data: { current_password: string; new_password: string; confirm_password: string }): Observable<any> {
    return this.getCsrfToken().pipe(
      switchMap(() => this.http.post(`${this.apiUrl}/change-password/`, data, { withCredentials: true })),
    );
  }
}