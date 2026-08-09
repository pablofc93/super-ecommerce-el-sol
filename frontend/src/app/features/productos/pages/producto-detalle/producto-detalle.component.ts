import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { ProductosService } from '../../services/productos.service';
import { Producto } from '../../models/producto.model';
import { CarritoService } from '../../../pedidos/services/carrito.service';
import { AuthService } from '../../../auth/services/auth.service';

@Component({
  selector: 'app-producto-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './producto-detalle.component.html',
  styleUrls: ['./producto-detalle.component.css']
})
export class ProductoDetalleComponent implements OnInit {

  producto!: Producto;
  loading = false;
  error: string | null = null;

  cantidad: number = 1;
  mensaje: string | null = null;
  mensajeEsError = false;
  agregando = false;

  // ✅ NUEVO
  esAdmin: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private productosService: ProductosService,
    private carritoService: CarritoService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id || isNaN(id)) {
      this.error = 'Producto inválido.';
      return;
    }

    // ✅ CORREGIDO (minúscula)
    const user = this.authService.getCurrentUser();
    this.esAdmin = user?.tipo_usuario === 'admin';

    this.loading = true;
    this.productosService.getProductoById(id).subscribe({
      next: (data) => {
        this.producto = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el producto.';
        this.loading = false;
      }
    });
  }

  agregarAlCarrito() {
    if (this.cantidad <= 0) {
      this.mensaje = 'Cantidad inválida.';
      this.mensajeEsError = true;
      return;
    }

    if (this.cantidad > this.producto.stock) {
      this.mensaje = 'No hay suficiente stock disponible.';
      this.mensajeEsError = true;
      return;
    }

    this.agregando = true;
    this.mensaje = null;
    this.mensajeEsError = false;

    this.carritoService.agregarProducto(this.producto.id, this.cantidad).subscribe({
      next: () => {
        this.mensaje = 'Producto agregado al carrito correctamente.';
        this.agregando = false;
      },
      error: (err) => {
        console.error(err);
        this.mensaje = 'Error al agregar producto al carrito.';
        this.mensajeEsError = true;
        this.agregando = false;
      }
    });
  }
}
