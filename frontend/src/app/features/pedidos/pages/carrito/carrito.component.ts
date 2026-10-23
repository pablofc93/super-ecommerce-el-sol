
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router';

import { CarritoService } from '../../services/carrito.service';
import { Carrito } from '../../models/carrito.model';

@Component({
  selector: 'app-carrito',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './carrito.component.html',
  styleUrls: ['./carrito.component.css'],
})
export class CarritoComponent implements OnInit {
  carrito: Carrito | null = null;
  loading = true;
  total = 0;
  montoPagado = 0;
  procesando = false;
  error: string | null = null;
  mensajeExito: string | null = null;

  /**
   * Dirección base del servidor Django.
   * Cambiala si tu backend utiliza otro host o puerto.
   */
  private readonly backendBaseUrl = 'http://localhost:8000';

  constructor(
    private carritoService: CarritoService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.carritoService.carrito$.subscribe((carrito) => {
      this.carrito = carrito;
      this.total = carrito
        ? this.carritoService.calcularTotal(carrito)
        : 0;
    });

    this.carritoService.getCarrito().subscribe({
      next: () => {
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  /**
   * Convierte la ruta relativa que devuelve Django
   * en una URL absoluta que el navegador pueda cargar.
   *
   * Ejemplo:
   * /media/productos/producto.png
   * -> http://localhost:8000/media/productos/producto.png
   */
  obtenerImagenUrl(
    imagenUrl: string | null | undefined,
  ): string | null {
    if (!imagenUrl) {
      return null;
    }

    // Si ya viene una URL absoluta, se utiliza directamente.
    if (/^https?:\/\//i.test(imagenUrl)) {
      return imagenUrl;
    }

    const ruta = imagenUrl.startsWith('/')
      ? imagenUrl
      : `/${imagenUrl}`;

    return `${this.backendBaseUrl}${ruta}`;
  }

  /**
   * Si una imagen no puede cargarse, se oculta para
   * que Angular muestre la alternativa con la inicial.
   */
  imagenError(event: Event): void {
    const imagen = event.target as HTMLImageElement;
    imagen.style.display = 'none';
  }

  eliminar(itemId: number): void {
    this.carritoService.eliminarItem(itemId).subscribe({
      next: () => {
        setTimeout(() => {
          const carritoActual =
            this.carritoService.getCarritoActual();

          if (!carritoActual || carritoActual.items.length === 0) {
            this.mensajeExito =
              'Carrito vaciado correctamente, gracias por elegirnos';

            setTimeout(() => {
              this.router.navigate(['/productos']);
            }, 2000);
          }
        }, 200);
      },
    });
  }

  vaciar(): void {
    this.error = null;
    this.mensajeExito = null;
    this.procesando = true;

    this.carritoService.vaciarCarrito().subscribe({
      next: () => {
        this.mensajeExito =
          'Carrito vaciado correctamente, gracias por elegirnos';

        this.procesando = false;

        if (this.carrito) {
          this.carrito.items = [];
        }

        this.total = 0;

        setTimeout(() => {
          this.carritoService.obtenerCarrito().subscribe({
            next: () => {
              this.router.navigate(['/']);
            },
          });
        }, 2000);
      },
      error: () => {
        this.error = 'Ocurrió un error al vaciar el carrito.';
        this.procesando = false;
      },
    });
  }

  confirmar(): void {
    this.error = null;
    this.mensajeExito = null;

    if (this.montoPagado < this.total) {
      this.error = 'El monto ingresado es menor al total del pedido.';
      return;
    }

    this.procesando = true;

    this.carritoService.confirmarPedido(this.montoPagado).subscribe({
      next: () => {
        this.mensajeExito =
          'Compra realizada con éxito, gracias por elegirnos';

        this.montoPagado = 0;
        this.total = 0;
        this.procesando = false;

        if (this.carrito) {
          this.carrito.items = [];
        }

        setTimeout(() => {
          this.carritoService.obtenerCarrito().subscribe({
            next: () => {
              this.router.navigate(['/']);
            },
          });
        }, 2000);
      },
      error: (err) => {
        this.error =
          err.error?.error || 'Ocurrió un error al confirmar el pedido.';
        this.procesando = false;
      },
    });
  }
}
