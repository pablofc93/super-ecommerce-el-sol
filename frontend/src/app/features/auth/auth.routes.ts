import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { AuthGuard } from './guards/auth.guard';

export const AuthRoutes: Routes = [
  { path: 'auth/login', component: LoginComponent },
  // { path: 'auth/register', component: RegisterComponent }, // futuro
];
