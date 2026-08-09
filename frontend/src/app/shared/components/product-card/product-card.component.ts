import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Producto } from '../../../features/productos/models/producto.model';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-card.component.html',
  styleUrls: ['./product-card.component.css']
})
export class ProductCardComponent {

  @Input() producto!: Producto;

  @Input() variant: 'default' | 'compact' = 'default';

  @Output() verDetalle = new EventEmitter<number>();

  onClick() {
    this.verDetalle.emit(this.producto.id);
  }
}