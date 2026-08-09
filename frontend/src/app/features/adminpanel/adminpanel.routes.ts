import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/guards/role.guard';
import { AdminpanelLayoutComponent } from './layout/adminpanel-layout.component';

export const ADMIN_PANEL_ROUTES: Routes = [
  {
    path: '',
    component: AdminpanelLayoutComponent,
    canActivate: [RoleGuard],
    data: { role: 'admin' },
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full',
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent,
          ),
      },
      {
        path: 'usuarios',
        loadComponent: () =>
          import('./pages/usuarios/usuarios.component').then(
            (m) => m.UsuariosComponent,
          ),
      },
      {
        path: 'productos',
        loadComponent: () =>
          import('./pages/productos/productos-admin.component').then(
            (m) => m.ProductosAdminComponent,
          ),
      },
      {
        path: 'pedidos',
        loadComponent: () =>
          import('./pages/pedidos/pedidos-admin.component').then(
            (m) => m.PedidosAdminComponent,
          ),
      },
      {
        path: 'reportes',
        loadComponent: () =>
          import('./pages/reportes/reportes.component').then(
            (m) => m.ReportesComponent,
          ),
      },
      {
        path: 'perfil',
        loadComponent: () =>
          import('./pages/perfil/perfil-admin.component').then(
            (m) => m.PerfilAdminComponent,
          ),
      },
      {
        path: 'categorias',
        loadComponent: () =>
          import('./pages/categorias/categorias.component').then(
            (m) => m.CategoriasComponent,
          ),
      },
    ],
  },
];
