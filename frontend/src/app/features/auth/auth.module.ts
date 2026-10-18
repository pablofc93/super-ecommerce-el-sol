/**
 * El objetivo de este archivo es organizar el módulo de autenticación y reunir los elementos necesarios
 * paralas funcionalidades de login y registro
 */

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common'; //proporciona funcionalidades que pueden utilizarse desde plantillas HTML
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms'; //permite utilizar los formularios reactivos
import { FormsModule } from '@angular/forms'; //funciones adicionales para formularios

import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';

@NgModule({ //decorador de TypeScript utilizdo por Angular

  //array que determina las funcionalidades del módulo
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,   // ✅ NECESARIO
    FormsModule,           // ✅ NECESARIO
    LoginComponent,        // standalone
    RegisterComponent      // standalone
  ],
  
  //array que determina que funcionalidades de este módulo se pueden utilizar desde otros módulos
  exports: [
    LoginComponent,
    RegisterComponent,
    ReactiveFormsModule,
    FormsModule
  ]
})
export class AuthModule {}