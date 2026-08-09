import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
import { ModalConfirmacionComponent } from '../../components/modal-confirmacion/modal-confirmacion.component';
import { AdminCategoriasService } from '../../services/admin-categorias.service';
import { AdminReportingService } from '../../services/admin-reporting.service';
import { CategoriaAdmin } from '../../models/categoria-admin.model';

@Component({
  selector: 'app-categorias',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    PaginationComponent,
    ModalConfirmacionComponent,
  ],
  templateUrl: './categorias.component.html',
})
export class CategoriasComponent implements OnInit {
  categorias: CategoriaAdmin[] = [];

  totalCategorias = 0;
  paginaActual = 1;
  totalPaginas = 0;
  pageSize = 15;

  searchTerm = '';

  categoriaAEliminar: number | null = null;

  nuevaCategoria = {
    nombre: '',
    descripcion: '',
  };

  categoriaEditando: CategoriaAdmin | null = null;

  loading = false;
  error: string | null = null;

  constructor(
    private categoriasService: AdminCategoriasService,
    private reportingService: AdminReportingService,
  ) {}

  ngOnInit(): void {
    this.reportingService.registrarAcceso('categorias').subscribe();
    this.cargarCategorias();
  }

  cargarCategorias(): void {
    this.loading = true;

    this.categoriasService
      .listarCategorias(this.paginaActual, this.searchTerm)
      .subscribe({
        next: (data) => {
          this.categorias = data.results;
          this.totalCategorias = data.count;
          this.totalPaginas = Math.ceil(this.totalCategorias / this.pageSize);
          this.loading = false;
        },
        error: () => {
          this.error = 'Error cargando categorías';
          this.loading = false;
        },
      });
  }

  buscar(): void {
    this.paginaActual = 1;
    this.cargarCategorias();
  }

  cambiarPagina(pagina: number): void {
    if (pagina < 1 || pagina > this.totalPaginas) return;
    this.paginaActual = pagina;
    this.cargarCategorias();
  }

  crearCategoria(): void {
    this.categoriasService.crearCategoria(this.nuevaCategoria).subscribe({
      next: () => {
        this.nuevaCategoria = {
          nombre: '',
          descripcion: '',
        };
        this.cargarCategorias();
      },
    });
  }

  editarCategoria(categoria: CategoriaAdmin): void {
    this.categoriaEditando = {
      ...categoria,
    };
  }

  guardarEdicion(): void {
    if (!this.categoriaEditando) return;

    this.categoriasService
      .actualizarCategoria(this.categoriaEditando.id, this.categoriaEditando)
      .subscribe({
        next: () => {
          this.categoriaEditando = null;
          this.cargarCategorias();
        },
      });
  }

  cancelarEdicion(): void {
    this.categoriaEditando = null;
  }

  abrirModalEliminar(id: number): void {
    this.categoriaAEliminar = id;
  }

  confirmarEliminacion(): void {
    if (!this.categoriaAEliminar) return;

    this.categoriasService
      .eliminarCategoria(this.categoriaAEliminar)
      .subscribe({
        next: () => {
          this.categoriaAEliminar = null;

          if (this.categorias.length === 1 && this.paginaActual > 1) {
            this.paginaActual--;
          }

          this.cargarCategorias();
        },
      });
  }
}
