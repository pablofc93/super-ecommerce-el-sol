import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Producto } from '../../../features/productos/models/producto.model';
import { ProductCardComponent } from '../product-card/product-card.component';

@Component({
  selector: 'app-product-grid',
  standalone: true,
  imports: [CommonModule, ProductCardComponent],
  templateUrl: './product-grid.component.html',
  styleUrls: ['./product-grid.component.css']
})
export class ProductGridComponent {

  @Input() productos: Producto[] = [];

  @Output() verDetalle = new EventEmitter<number>();

  abrirDetalle(id: number) {
    this.verDetalle.emit(id);
  }

}