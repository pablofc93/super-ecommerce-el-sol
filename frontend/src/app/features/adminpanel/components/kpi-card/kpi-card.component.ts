import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './kpi-card.component.html'
})
export class KpiCardComponent {
  @Input() titulo: string = '';
  @Input() valor: number | string = '';

  get valorFormateado() {
    if (this.titulo.includes('Ventas') && typeof this.valor === 'number') {
      return `$ ${this.valor.toLocaleString('es-AR', { minimumFractionDigits: 2 })}`;
    }
    if (typeof this.valor === 'number') {
      return this.valor.toLocaleString();
    }
    return this.valor;
  }
}