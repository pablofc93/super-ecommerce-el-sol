import { Routes } from '@angular/router';
import { PublicLayoutComponent } from './layout/public-layout/public-layout.component';
import { LoginComponent } from './features/auth/pages/login/login.component';
import { RegisterComponent } from './features/auth/pages/register/register.component';

import { PerfilComponent } from './features/clientes/pages/perfil/perfil.component';

import { HomeComponent } from './features/home/pages/home/home.component';
import { CarritoComponent } from './features/pedidos/pages/carrito/carrito.component';
import { MisPedidosComponent } from './features/pedidos/pages/mis-pedidos/mis-pedidos.component';

import { AuthGuard } from './features/auth/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: PublicLayoutComponent,
    children: [
      { path: '', component: HomeComponent },

      {
        path: 'productos',
        loadChildren: () =>
          import('./features/productos/productos.routes')
            .then(m => m.productosRoutes)
      },

      {
        path: 'carrito',
        component: CarritoComponent,
        canActivate: [AuthGuard]
      },

      {
        path: 'mis-pedidos',
        component: MisPedidosComponent,
        canActivate: [AuthGuard]
      }
    ]
  },

  // -----------------------------
  // AUTH
  // -----------------------------

  { path: 'auth/login', component: LoginComponent },
  { path: 'auth/register', component: RegisterComponent },

  // -----------------------------
  // PERFIL CLIENTE
  // -----------------------------

  {
    path: 'clientes/perfil',
    component: PerfilComponent,
    canActivate: [AuthGuard]
  },

  // -----------------------------
  // PANEL ADMIN
  // -----------------------------

  {
    path: 'admin',
    loadChildren: () =>
      import('./features/adminpanel/adminpanel.routes')
        .then(m => m.ADMIN_PANEL_ROUTES)
  },

  { path: '**', redirectTo: '' }
];