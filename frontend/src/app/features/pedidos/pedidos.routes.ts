import { Routes } from '@angular/router';
import { CarritoComponent } from './pages/carrito/carrito.component';

/**cuando el usuario accede a /carrito angular carga CarritoComponent */
export const PEDIDOS_ROUTES: Routes = [
  {
    path: 'carrito',
    component: CarritoComponent
  }
];
