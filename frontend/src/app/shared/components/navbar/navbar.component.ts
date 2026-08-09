import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

import { AuthService } from '../../../features/auth/services/auth.service';
import { CarritoService } from '../../../features/pedidos/services/carrito.service';
import { SidebarService } from '../../services/sidebar.service';

import { User } from '../../../features/auth/models/user.model';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {
  // Usuario actual
  currentUser: User | null = null;

  // Cantidad productos carrito
  cantidadCarrito = 0;

  // Control menú móvil
  menuAbierto = false;

  constructor(
    public authService: AuthService,
    private carritoService: CarritoService,
    private sidebarService: SidebarService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // ============================
    // USUARIO LOGUEADO
    // ============================

    this.authService.user$
      .subscribe(user => {
        this.currentUser = user;
      });

    // ============================
    // CONTADOR CARRITO
    // ============================

    this.carritoService.carrito$
      .subscribe(carrito => {
        this.cantidadCarrito =
          carrito
            ? this.carritoService.obtenerCantidadTotal(carrito)
            : 0;
      });
  }

  // ============================
  // ESTADOS DEL MENU
  // ============================

  get isLoggedIn(): boolean {
    return this.currentUser !== null;
  }

  get isAdmin(): boolean {
    return this.currentUser?.tipo_usuario === 'admin';
  }

  get isCliente(): boolean {
    return this.currentUser?.tipo_usuario === 'cliente'
      || this.currentUser?.tipo_usuario === 'usuario';
  }

  get esVistaCategorias(): boolean {
    const url = this.router.parseUrl(this.router.url);
    const segmentos = url.root.children['primary']?.segments ?? [];

    return (
      segmentos.map((segmento) => segmento.path).join('/') === 'productos' &&
      url.queryParams['view'] === 'categories'
    );
  }

  get esVistaProductos(): boolean {
    return this.router.url.startsWith('/productos') && !this.esVistaCategorias;
  }

  // ============================
  // ACCIONES
  // ============================

  abrirCategorias(): void {
    this.sidebarService.close();
    this.cerrarMenu();
    this.router.navigate(['/productos'], {
      queryParams: { view: 'categories' }
    });
  }

  cerrarMenu(): void {
    this.menuAbierto = false;
  }

  logout(): void {
    this.authService.logout()
      .subscribe(() => {
        this.cerrarMenu();
        this.router.navigate(['/']);
      });
  }
}
