import { Routes } from '@angular/router';
import { ProductosListComponent } from './pages/productos-list/productos-list.component';
import { ProductoDetalleComponent } from './pages/producto-detalle/producto-detalle.component';
import { AuthGuard } from '../auth/guards/auth.guard';

export const productosRoutes: Routes = [
  {
    path: '',
    component: ProductosListComponent
  },

  {
    path: ':id',
    component: ProductoDetalleComponent,
    canActivate: [AuthGuard] // 🔥 PROTECCIÓN
  }
];