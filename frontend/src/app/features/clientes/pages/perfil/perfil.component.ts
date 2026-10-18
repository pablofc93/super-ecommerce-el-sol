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
  perfil: ClientePerfil | null = null; // contiene los datos del cliente obtenidos desde el backend
  editMode = false; // indica si el usuario está editando su perfil o no

  password = ''; // almacena la nueva contraseña que el usuario quiere establecer
  confirmPassword = ''; // almacena la confirmación de la nueva contraseña que el usuario quiere establecer

  errors: any = {}; // contiene los errores de validación devueltos por el backend al intentar actualizar el perfil

  constructor(
    private clienteService: ClienteService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.clienteService.getPerfil().subscribe({ // el componente solicita a ClienteService los datos del perfil del cliente al inicializarse
      next: (data) => {
        this.perfil = data; // en perfil se almaceanan los datos del clientes obtenidos desde el backend
      },
      error: (err) => {
        console.error('Error cargando perfil', err); // si ocurre un error al cargar el perfil, se muestra un mensaje de error en la consola
      },
    });
  }
  
  /**CAMBIAR A MODO DE EDICIÓN O VISUALIZACIÓN*/
  toggleEdit() {
      this.editMode = !this.editMode;

    if (!this.editMode) {
      this.password = '';
      this.confirmPassword = '';
      this.errors = {};
    }
  }

  // este método se encarga de navegar a la página de productos cuando el usuario hace clic en "volver"
  volver() {
    this.router.navigate(['/productos']);
  }

  save() {
    if (!this.perfil) return; /**si no hay perfil, el método finaliza */

    this.errors = {}; //se limpian los errores de validación previos antes de intentar actualizar el perfil
    
    /**se valida si el usuario ingresó una contraseña y
     * además valida si la contraseña ingresada y la confirmación de esa contraseña coinciden
     * si no coinciden, se agrega un error al objeto errors y se retorna el método sin intentar
     * actualizar el perfil y no se realiza la solicitud al backend para actualizar el perfil
     */
    if (this.password && this.password !== this.confirmPassword) {
      this.errors.password = ['Las contraseñas no coinciden'];
      return;
    }
    
    /**se construye el objeto de datos que será enviado al backend
     * para actualizar el perfil
     */
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
    
    /**se evalúa si el usuario ha ingresado una contraseña
     * si no ha ingresado, no se envía la contraseña al backend
     * y el perfil se actualiza sin cambiar la contraseña
     */
    if (this.password) {
      data.password = this.password;
    }
    
    /**se envía la solicitud al backend para actualizar el perfil */
    this.clienteService.updatePerfil(data).subscribe({
      next: (res: any) => {
        
        /**se verifica si existe una nueva contraseña
         * si existe, se cierra la sesión del usuario y se redirige a la
         * página de inicio de sesión para que el usuario vuelva a iniciar 
         * sesión con la nueva contraseña
         */
        if (this.password) {
          alert('Contraseña actualizada. Debes iniciar sesión nuevamente.');

          this.authService.logout().subscribe(() => {
            this.router.navigate(['/login']);
          });

          return;
        }
        
        /**se actualiza el perfil con los datos recibidos del backend */
        this.perfil = res;

        
        this.editMode = false;

        this.password = '';
        this.confirmPassword = '';
        this.errors = {};

        alert('Perfil actualizado correctamente');

        this.router.navigate(['/productos']);
      },
      
      /** manejo de errores */
      error: (err) => {
        console.error('Error actualizando perfil', err);
        
        /**se verifica si el error contiene mensajes de validación */
        if (err.error) {
          this.errors = err.error; /* el objeto errors es utilizado para mostrar los mensajes de error en la plantilla HTML */
        }
      },
    });
  }
}