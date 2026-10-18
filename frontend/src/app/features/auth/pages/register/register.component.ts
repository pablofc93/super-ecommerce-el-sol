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
  
  /**
   * Este método se ejecuta cuando el usuario envía el formulario
   * con los datos de registros para almacenar el nuevo usuario
   * del sistema 
   */
  onSubmit() {
    
    //se comprueba si el formato del formulario es válido
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched(); //esto permite que la plantilla muestre los mensajes de validación
      return;
    }

    this.loading = true;
    this.errorMessages = [];
    
    //si el formulario es válido, se envían los datos al servicio
    this.authService.register(this.registerForm.value).subscribe({
      
      /**
       * si el registro es exitoso se muestra un modal de Bootstrap
       */
      next: () => {
        this.loading = false;
        this.errorMessages = [];

        // Aquí se obtiene el modal de Bootstrap
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

  /** 
   * este método transforma las respuestas de error del backend en una
   * lista de mensajes que pueden mostrarse fácilmente en la interfaz
   */
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
  
  /**
   * este método convierte nombres técnicos utilizados por el backend en
   * nombres más comprensibles para el usuario
   */
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