import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';

import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,   // ✅ NECESARIO
    FormsModule,           // ✅ NECESARIO
    LoginComponent,        // standalone
    RegisterComponent      // standalone
  ],
  exports: [
    LoginComponent,
    RegisterComponent,
    ReactiveFormsModule,
    FormsModule
  ]
})
export class AuthModule {}