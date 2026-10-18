import { Routes } from '@angular/router';
import { ProductosListComponent } from './pages/productos-list/productos-list.component';
import { ProductoDetalleComponent } from './pages/producto-detalle/producto-detalle.component';
import { AuthGuard } from '../auth/guards/auth.guard';

export const productosRoutes: Routes = [
  {
    path: '', // ruta principal del módulo de productos, en este caso muestra la lista de productos
    component: ProductosListComponent
  },

  {
    path: ':id', // :id representa un parámetro dinámico de la url ej: /productos/15
    component: ProductoDetalleComponent,
    canActivate: [AuthGuard] // para acceder a este componente el usuario debe estar logueado(autenticado)
  }
];