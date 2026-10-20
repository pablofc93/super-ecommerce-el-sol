import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, catchError, of, switchMap, finalize, map } from 'rxjs';
import { Router } from '@angular/router';
import { User } from '../models/user.model';
import { environment } from '../../../../environments/environment';
import { CarritoService } from '../../pedidos/services/carrito.service';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly csrfUrl = `${environment.apiUrl}/csrf/`;
  private userSubject = new BehaviorSubject<User | null>(null); // permite mantener al usuario autenticado
  public user$ = this.userSubject.asObservable(); // determina cuando un usuario no está autenticado
  private initializedSubject = new BehaviorSubject<boolean>(false); // para determinar si ya se terminó de comprobar la sesión existente
  public initialized$ = this.initializedSubject.asObservable(); 
  private apiUrl = `${environment.apiUrl}/auth`; // URL base para los endpoints de autenticación

  constructor(
    private http: HttpClient,
    private router: Router,
    private carritoService: CarritoService,
  ) {}
  
  /**
   * Solicita un token CSRF para las solicitudes que modifican datos.
   */
  private getCsrfToken(): Observable<string> {
    return this.http
      .get<{ csrfToken: string }>(this.csrfUrl, { withCredentials: true })
      .pipe(map(({ csrfToken }) => csrfToken));
  }

  private csrfHeaders(token: string): HttpHeaders {
    return new HttpHeaders({ 'X-CSRFToken': token });
  }

  // =========================
  // REGISTER
  // =========================
  register(data: { username: string; first_name: string; last_name: string; email: string; password: string }): Observable<User> {
    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.post<User>(`${this.apiUrl}/register/`, data, {
          headers: this.csrfHeaders(token),
          withCredentials: true,
        })
      ),
      
      /* 
      * luego de registrar al usuario, se ejecuta automáticamente 
      * el proceso de login con el usuario 
      * y contraseña proporcionados en el registro
       */
      switchMap(() => this.login(data.username, data.password)), 
    );
  }

  // =========================
  // LOGIN
  // =========================
  login(username: string, password: string): Observable<User> {
    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.post<User>(
          `${this.apiUrl}/login/`,
          { username, password },
          {
            headers: this.csrfHeaders(token),
            withCredentials: true,
          }
        )
      ),
      tap((user) => {
        // Cuando el backend responde correctamente, tap guardar usuario autenticado
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
    return this.http.post(`${environment.apiUrl}/auth/logout/`, {}, { withCredentials: true }).pipe( //se envía solicitud al back
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
      tap((user) => { //si se obtiene el usuario del back, se ejecutan las siguientes acciones
        this.userSubject.next(user); //almacena el usuario actual como autenticado
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
      switchMap((token) =>
        this.http.patch<User>(`${this.apiUrl}/me/`, data, {
          headers: this.csrfHeaders(token),
          withCredentials: true,
        })
      ),
      tap((updatedUser) => this.userSubject.next(updatedUser)), //si Django devuelve el usuario actualizado, se almacena en updateUser
    );
  }
  /**
   * Al iniciar la aplicación consulta a Django si existe una sesión.
   * Cuando termine esa comprobación, independientemente de si había o no una sesión,
   * marca la autenticación como inicializada
   */
  initializeAuth(): void {
    this.getMe().pipe(finalize(() => this.initializedSubject.next(true))).subscribe();
  }
  
  //permite comprobar si existe un usuario autenticado
  isLoggedIn(): boolean {
    return this.userSubject.value !== null;
  }
  
  //permite obtener el usuario actual
  getCurrentUser(): User | null {
    return this.userSubject.value;
  }
  
  //método que envía la solicitud al backend para el cambio de contraseña
  changePassword(data: { current_password: string; new_password: string; confirm_password: string }): Observable<any> {
    return this.getCsrfToken().pipe(
      switchMap((token) =>
        this.http.post(`${this.apiUrl}/change-password/`, data, {
          headers: this.csrfHeaders(token),
          withCredentials: true,
        })
      ),
    );
  }
}