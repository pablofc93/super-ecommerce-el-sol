import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../features/auth/services/auth.service';

@Component({
  selector: 'app-adminpanel-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './adminpanel-layout.component.html',
  styleUrl: './adminpanel-layout.component.css'
})
export class AdminpanelLayoutComponent {

  sidebarVisible = false; // Variable que controla la visibilidad del sidebar (menú lateral) en el panel de administración. Inicialmente está oculto (false).

  /**en el constructor se define la inyección de dependencias */
  constructor(
    private authService: AuthService, //permite acceder a los métodos del servicio de autenticación, como el logout
    private router: Router // permite redirigir al usuario a diferentes rutas de la aplicación, como el home después del logout
  ) {}

  logout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/']); // 🔥 redirige al home
    });
  }
}