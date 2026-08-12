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

  @Input() producto!: Producto;

  @Input() variant: 'default' | 'compact' = 'default';

  @Output() verDetalle = new EventEmitter<number>();

  mostrarModalLogin = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onClick(): void {

    if (!this.authService.isLoggedIn()) {
      this.mostrarModalLogin = true;
      return;
    }

    this.verDetalle.emit(this.producto.id);
  }

  cerrarModalLogin(): void {
    this.mostrarModalLogin = false;
  }

  irAlLogin(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/login']);
  }

  irAlRegistro(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/register']);
  }
}