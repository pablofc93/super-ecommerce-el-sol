import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';
import { User } from '../../models/user.model';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class LoginComponent {

  loginForm: FormGroup; //propiedad que se utiliza para asociar este formulario a la plantilla HTML
  error: string | null = null;
  cargando = false;
  
  //construcción del formulario
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required], //se crea campo de usernane obligatorio
      password: ['', Validators.required] //se crea campo de password obligatorio
    });
  }
  
  /**
   * este método se ejecuta cuando el usuario intenta iniciar sesión
   */
  submit(): void {
    //verifica si el formulario es válido o si ya está procesando un login
    //esto evita enviar información incompleta y que se envíen múltiples solicitudes
    //mientras una todavía sigue siendo procesada
    if (this.loginForm.invalid || this.cargando) {
      return;
    }
  
    this.error = null;
    this.cargando = true;
  
    // Forzar a Angular a renderizar el spinner antes de iniciar la petición
    this.cdr.detectChanges();
    
    //luego del login se obtiene el usuario y contraseña
    const { username, password } = this.loginForm.value;
  
    setTimeout(() => {
      
      //se envía la información correspondiente al usuario y contraseña
      // al servicio de autenticación para que se procese el login
      this.authService.login(username, password).subscribe({

         /**si la autenticación es exitosa, se redirige a /admin o a /productos según corresponda*/
        next: (user: User) => {
          this.cargando = false;
          if (user.tipo_usuario === 'admin') {
            this.router.navigate(['/admin']);
          } else {
            this.router.navigate(['/productos']);
          }
        },
  
        error: (err) => {
  
          this.cargando = false;
          this.error = err.error?.error || 'Error de login';
  
        }
  
      });
  
    }, 0);
  }
}