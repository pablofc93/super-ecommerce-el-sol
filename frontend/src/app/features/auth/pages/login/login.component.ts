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

  loginForm: FormGroup;
  error: string | null = null;
  cargando = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  submit(): void {
    if (this.loginForm.invalid || this.cargando) {
      return;
    }
  
    this.error = null;
    this.cargando = true;
  
    // Forzar a Angular a renderizar el spinner antes de iniciar la petición
    this.cdr.detectChanges();
  
    const { username, password } = this.loginForm.value;
  
    setTimeout(() => {
  
      this.authService.login(username, password).subscribe({
  
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