import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-modal-confirmacion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modal-confirmacion.component.html'
})
export class ModalConfirmacionComponent {

  @Input() titulo: string = 'Confirmar acción';
  @Input() mensaje: string = '¿Estás seguro?';

  @Output() confirmar = new EventEmitter<void>();
  @Output() cancelar = new EventEmitter<void>();

  cerrar() {
    this.cancelar.emit();
  }

  confirmarAccion() {
    this.confirmar.emit();
  }

}