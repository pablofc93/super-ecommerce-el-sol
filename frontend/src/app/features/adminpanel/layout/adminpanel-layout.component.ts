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

  sidebarVisible = false;

  constructor(
    private authService: AuthService,
    private router: Router // 🔥 agregado
  ) {}

  logout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/']); // 🔥 redirige al home
    });
  }
}