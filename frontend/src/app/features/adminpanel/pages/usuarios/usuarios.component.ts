import { Component, OnInit } from '@angular/core';
import { AdminUsuariosService } from '../../services/admin-usuarios.service';
import { UsuarioAdmin } from '../../models/usuario-admin.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModalConfirmacionComponent } from '../../components/modal-confirmacion/modal-confirmacion.component';
import { AdminReportingService } from '../../services/admin-reporting.service'; // 🔥 IMPORTAR
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-usuarios-admin',
  standalone: true,
  templateUrl: './usuarios.component.html',
  imports: [
    CommonModule,
    FormsModule,
    ModalConfirmacionComponent,
    PaginationComponent,
  ],
})
export class UsuariosComponent implements OnInit {
  usuarios: UsuarioAdmin[] = [];

  totalUsuarios = 0;
  paginaActual = 1;
  totalPaginas = 0;
  pageSize = 5;

  searchTerm = '';

  usuarioAEliminar: number | null = null;

  nuevoUsuario = {
    username: '',
    email: '',
    password: '',
    tipo_usuario: 'cliente' as 'admin' | 'cliente',
  };

  loading = false;
  error: string | null = null;

  constructor(
    private usuariosService: AdminUsuariosService,
    private reportingService: AdminReportingService, // 🔥 INYECTAR
  ) {}

  ngOnInit(): void {
    this.reportingService.registrarAcceso('usuarios').subscribe(); // 🔥 REGISTRAR
    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.loading = true;

    this.usuariosService
      .listarUsuarios(this.paginaActual, this.searchTerm)
      .subscribe({
        next: (data) => {
          this.usuarios = data.results;
          this.totalUsuarios = data.count;

          this.totalPaginas = Math.ceil(this.totalUsuarios / this.pageSize);

          this.loading = false;
        },
        error: () => {
          this.error = 'Error cargando usuarios';
          this.loading = false;
        },
      });
  }

  buscar(): void {
    this.paginaActual = 1;
    this.cargarUsuarios();
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina < 1 || nuevaPagina > this.totalPaginas) return;
    this.paginaActual = nuevaPagina;
    this.cargarUsuarios();
  }

  crearUsuario(): void {
    this.usuariosService.crearUsuario(this.nuevoUsuario).subscribe({
      next: () => {
        this.cargarUsuarios();
        this.nuevoUsuario = {
          username: '',
          email: '',
          password: '',
          tipo_usuario: 'cliente',
        };
      },
    });
  }

  cambiarRol(usuario: UsuarioAdmin): void {
    const nuevoRol = usuario.tipo_usuario === 'admin' ? 'cliente' : 'admin';

    this.usuariosService.cambiarRol(usuario.id, nuevoRol).subscribe({
      next: () => this.cargarUsuarios(),
    });
  }

  abrirModalEliminar(id: number): void {
    this.usuarioAEliminar = id;
  }

  confirmarEliminacion(): void {
    if (!this.usuarioAEliminar) return;

    this.usuariosService.eliminarUsuario(this.usuarioAEliminar).subscribe({
      next: () => {
        this.usuarioAEliminar = null;

        if (this.usuarios.length === 1 && this.paginaActual > 1) {
          this.paginaActual--;
        }

        this.cargarUsuarios();
      },
    });
  }
}
