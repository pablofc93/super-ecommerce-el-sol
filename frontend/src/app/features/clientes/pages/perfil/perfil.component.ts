import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { AuthService } from '../../../auth/services/auth.service';

import {
  ClienteService,
  ClientePerfil,
} from '../../../clientes/services/cliente.service';

@Component({
  selector: 'app-perfil',
  templateUrl: './perfil.component.html',
  standalone: true,
  imports: [CommonModule, FormsModule],
})
export class PerfilComponent implements OnInit {
  perfil: ClientePerfil | null = null;
  editMode = false;

  password = '';
  confirmPassword = '';

  errors: any = {};

  constructor(
    private clienteService: ClienteService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.clienteService.getPerfil().subscribe({
      next: (data) => {
        this.perfil = data;
      },
      error: (err) => {
        console.error('Error cargando perfil', err);
      },
    });
  }

  toggleEdit() {
    this.editMode = !this.editMode;

    if (!this.editMode) {
      this.password = '';
      this.confirmPassword = '';
      this.errors = {};
    }
  }

  // 🔥 NUEVO MÉTODO
  volver() {
    this.router.navigate(['/productos']);
  }

  save() {
    if (!this.perfil) return;

    this.errors = {};

    if (this.password && this.password !== this.confirmPassword) {
      this.errors.password = ['Las contraseñas no coinciden'];
      return;
    }

    const data: any = {
      username: this.perfil.username,
      email: this.perfil.email,
      first_name: this.perfil.first_name,
      last_name: this.perfil.last_name,
      telefono: this.perfil.telefono,
      direccion: this.perfil.direccion,
      ciudad: this.perfil.ciudad,
      provincia: this.perfil.provincia,
      codigo_postal: this.perfil.codigo_postal,
    };

    if (this.password) {
      data.password = this.password;
    }

    this.clienteService.updatePerfil(data).subscribe({
      next: (res: any) => {

        if (this.password) {
          alert('Contraseña actualizada. Debes iniciar sesión nuevamente.');

          this.authService.logout().subscribe(() => {
            this.router.navigate(['/login']);
          });

          return;
        }

        this.perfil = res;
        this.editMode = false;

        this.password = '';
        this.confirmPassword = '';
        this.errors = {};

        alert('Perfil actualizado correctamente');

        this.router.navigate(['/productos']);
      },

      error: (err) => {
        console.error('Error actualizando perfil', err);

        if (err.error) {
          this.errors = err.error;
        }
      },
    });
  }
}