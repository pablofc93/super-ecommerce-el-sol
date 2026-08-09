import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

declare var bootstrap: any; // 👈 necesario para usar modal

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html',
})
export class RegisterComponent {

  registerForm: FormGroup;
  loading = false;

  errorMessages: string[] = [];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
  ) {
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  onSubmit() {

    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.errorMessages = [];

    this.authService.register(this.registerForm.value).subscribe({

      next: () => {
        this.loading = false;
        this.errorMessages = [];

        // 🔥 mostrar modal bonito
        const modal = new bootstrap.Modal(
          document.getElementById('successModal')
        );
        modal.show();
      },

      error: (err) => {
        console.error('ERROR REGISTRO:', err);

        this.loading = false;
        this.errorMessages = this.formatErrors(err?.error);
      },

    });

  }

  // =========================
  private formatErrors(error: any): string[] {

    if (!error) return ['Error desconocido'];

    if (typeof error.detail === 'string') {
      return [error.detail];
    }

    if (typeof error === 'object') {
      return Object.entries(error).flatMap(([field, messages]: any) => {

        if (Array.isArray(messages)) {
          return messages.map(
            (msg: string) => `${this.humanizeField(field)}: ${msg}`
          );
        }

        return [`${this.humanizeField(field)}: ${messages}`];
      });
    }

    return ['Error al registrarse'];
  }

  private humanizeField(field: string): string {

    const map: any = {
      email: 'Email',
      username: 'Usuario',
      password: 'Contraseña',
      first_name: 'Nombre',
      last_name: 'Apellido',
    };

    return map[field] || field;
  }

  // 🔥 redirigir después de cerrar modal
  goToProductos() {
    this.router.navigate(['/productos']);
  }

}