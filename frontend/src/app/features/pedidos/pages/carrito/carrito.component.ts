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

  /**propiedades del componente carrito */
  carrito: Carrito | null = null;
  loading = true;
  total = 0;
  montoPagado: number = 0;
  procesando = false;
  error: string | null = null;
  mensajeExito: string | null = null;

  constructor(
    private carritoService: CarritoService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.carritoService.carrito$.subscribe((carrito) => { //se sucribe al servicio carritoService para obtener el carrito actualizado
      this.carrito = carrito; // almacena el carrito recibido en la propiedad carrito del componente
      this.total = carrito ? this.carritoService.calcularTotal(carrito) : 0; //calcula el total del carrito utilizando el método calcularTotal del servicio carritoService
    });
    
    /*obtiene el carrito actual del usuario desde el backend y actualiza la propiedad loading a false
     cuando se completa la operación, ya sea con éxito o con error. 
     Esto permite que la interfaz de usuario refleje el 
     estado de carga del carrito de manera adecuada
    */
    this.carritoService.getCarrito().subscribe({
      next: () => (this.loading = false),
      error: () => (this.loading = false),
    });
  }

  // Eliminación de producos desde el carrito
  eliminar(itemId: number) {
    this.carritoService.eliminarItem(itemId).subscribe({ // se suscribe al método eliminarItem del servicioCarritoService para eliminar un item del carrito
      next: () => {
        // ⏱ Esperar a que el backend actualice el carrito
        setTimeout(() => {
          //se obtiene el carrito actual
          const carritoActual = this.carritoService.getCarritoActual();
          
          /**se verifica si el carrito actual es null o si no tiene productos */
          if (!carritoActual || carritoActual.items.length === 0) {

            // ✅ Mostrar mensaje UNA sola vez
            this.mensajeExito =
              'Carrito vaciado correctamente, gracias por elegirnos';

            // ⏱ Redirección
            setTimeout(() => {
              this.router.navigate(['/productos']);
            }, 2000);
          }
        }, 200);
      }
    });
  }

  vaciar() {
    /**limpia las variables de cualquier estado anterior */
    this.error = null;
    this.mensajeExito = null;
    this.procesando = true; //permite deshabilitar botones y mostrar un spinner mientras se procesa la acción de vaciar el carrito

    this.carritoService.vaciarCarrito().subscribe({ //se llama al método vaciarCarrito del servicio carritoService
      next: () => {
        /**si la operación es correcta, 
         * se muestra un mensaje de éxito 
         * habilita nuevamente los botones
         * vacía el carrito, carrito.items = []
         * actualiza el total a 0
         * luego de 2 segundos, se obtiene nuevamente el carrito ya actualizado y se redirige al usuario a la página principal
         * */
        this.mensajeExito =
          'Carrito vaciado correctamente, gracias por elegirnos';

        this.procesando = false;
        
        /**se verifica que el el carrito exista
         * si existe, se vacía el arreglo de items del carrito
         */
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
  
  /**CONFIRMAR UNA COMPRA */
  confirmar() {
    this.error = null;
    this.mensajeExito = null;
    
    /**evalúa que el monto ingresado sea suficiente */
    if (this.montoPagado < this.total) {
      this.error = 'El monto ingresado es menor al total del pedido.';
      return;
    }
    
    /**si el monto procesado es suficiente, se inicia el proceso de confirmación
     * primero desactiva todos los botones de la interfaz de usuario
     * y muestra el spinner de carga mientras se procesa la confirmación del pedido
     */
    this.procesando = true;

    this.carritoService.confirmarPedido(this.montoPagado).subscribe({
      next: () => {
        this.mensajeExito = 'Compra realizada con éxito, gracias por elegirnos';

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
