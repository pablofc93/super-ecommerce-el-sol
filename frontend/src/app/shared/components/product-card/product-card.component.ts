import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { Producto } from '../../../features/productos/models/producto.model';
import { AuthService } from '../../../features/auth/services/auth.service';
import { ModalAutenticacionComponent } from '../../modal-autenticacion/modal-autenticacion.component';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ModalAutenticacionComponent
  ],
  templateUrl: './product-card.component.html',
  styleUrls: ['./product-card.component.css']
})
export class ProductCardComponent {

  // Recibe el producto que debe mostrar la tarjeta.
  @Input() producto!: Producto;

  // Permite elegir el estilo visual de la tarjeta.
  @Input() variant: 'default' | 'compact' = 'default';

  // Emite el ID del producto al componente padre.
  @Output() verDetalle = new EventEmitter<number>();

  // Controla la visibilidad del modal de autenticación.
  mostrarModalLogin = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  /**
   * Se ejecuta cuando se hace clic en la tarjeta.
   * Si el usuario no está autenticado, muestra el modal.
   * Si está autenticado, emite el ID del producto.
   */
  onClick(): void {
    if (!this.authService.isLoggedIn()) {
      this.mostrarModalLogin = true;
      return;
    }

    this.verDetalle.emit(this.producto.id);
  }

  // Cierra el modal de autenticación.
  cerrarModalLogin(): void {
    this.mostrarModalLogin = false;
  }

  // Cierra el modal y navega al login.
  irAlLogin(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/login']);
  }

  // Cierra el modal y navega al registro.
  irAlRegistro(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/register']);
  }

}