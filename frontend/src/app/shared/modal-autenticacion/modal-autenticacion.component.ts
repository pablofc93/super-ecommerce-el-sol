import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-modal-autenticacion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modal-autenticacion.component.html'
})
export class ModalAutenticacionComponent {

  @Input() titulo: string = 'Iniciar sesión';

  @Input() mensaje: string =
    'Para poder comprar se necesita ingresar al sistema.';

  @Output() ingresar = new EventEmitter<void>();

  @Output() registrarse = new EventEmitter<void>();

  @Output() cerrar = new EventEmitter<void>();

  onIngresar(): void {
    this.ingresar.emit();
  }

  onRegistrarse(): void {
    this.registrarse.emit();
  }

  onCerrar(): void {
    this.cerrar.emit();
  }
}