import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../auth/services/auth.service';

@Component({
  selector: 'app-perfil-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './perfil-admin.component.html',
})
export class PerfilAdminComponent implements OnInit {
  user: any = {};

  passwordData = {
    current_password: '',
    new_password: '',
    confirm_password: '',
  };

  message: string = '';
  error: string = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.getMe().subscribe((user) => {
      this.user = user;
    });
  }

  guardarPerfil() {
    this.message = '';
    this.error = '';

    this.authService
      .updateMe({
        username: this.user.username,
        email: this.user.email,
      })
      .subscribe({
        next: () => (this.message = 'Perfil actualizado correctamente'),
        error: () => (this.error = 'Error al actualizar perfil'),
      });
  }

  cambiarPassword() {
    this.message = '';
    this.error = '';

    this.authService.changePassword(this.passwordData).subscribe({
      next: (res: any) => {
        this.message = res.message;

        // 🔥 redirigir al login
        this.authService.forceLogout();
      },
      error: (err) => {
        const errors = err.error;

        if (errors.confirm_password) {
          this.error = errors.confirm_password[0];
        } else if (errors.current_password) {
          this.error = errors.current_password[0];
        } else if (errors.new_password) {
          this.error = errors.new_password[0];
        } else {
          this.error = 'Ocurrió un error';
        }
      },
    });
  }
}
