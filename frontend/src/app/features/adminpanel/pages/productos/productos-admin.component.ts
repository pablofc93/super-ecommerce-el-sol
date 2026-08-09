import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminReportingService } from '../../services/admin-reporting.service';

import { AdminProductosService } from '../../services/admin-productos.service';
import { CategoriasService } from '../../../productos/services/categorias.service';

import { ProductoAdmin } from '../../models/producto-admin.model';
import { Categoria } from '../../../productos/models/categoria.model';

import { ModalConfirmacionComponent } from '../../components/modal-confirmacion/modal-confirmacion.component';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-productos-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ModalConfirmacionComponent,
    PaginationComponent,
  ],
  templateUrl: './productos-admin.component.html',
})
export class ProductosAdminComponent implements OnInit {
  productos: ProductoAdmin[] = [];
  categorias: Categoria[] = [];

  productoActual: ProductoAdmin = this.nuevoProducto();

  mostrarFormulario = false;
  modoEdicion = false;

  productoAEliminar: number | null = null;

  imagenSeleccionada: File | null = null;

  // =========================
  // PAGINACION
  // =========================

  totalProductos = 0;
  paginaActual = 1;
  totalPaginas = 0;

  // mismo tamaño que Django REST
  pageSize = 15;

  searchTerm = '';

  loading = false;

  constructor(
    private productosService: AdminProductosService,
    private categoriasService: CategoriasService,
    private reportingService: AdminReportingService, // 🔥
  ) {}

  ngOnInit(): void {
    this.reportingService.registrarAcceso('productos').subscribe(); // 🔥
    this.cargarProductos();
    this.cargarCategorias();
  }

  nuevoProducto(): ProductoAdmin {
    return {
      nombre: '',
      descripcion: '',
      precio: 0,
      stock: 0,
      categoria_id: undefined,
    };
  }

  cargarCategorias(): void {
    this.categoriasService.listar().subscribe({
      next: (data) => (this.categorias = data),
      error: (err) => console.error('Error cargando categorias', err),
    });
  }

  cargarProductos(): void {
    this.loading = true;

    this.productosService.listar(this.paginaActual, this.searchTerm).subscribe({
      next: (data) => {
        if (data.results) {
          this.productos = data.results;
          this.totalProductos = data.count;
        } else {
          this.productos = data;
          this.totalProductos = data.length;
        }

        this.totalPaginas = Math.max(
          1,
          Math.ceil(this.totalProductos / this.pageSize)
        );
        
        if (this.paginaActual > this.totalPaginas) {
          this.paginaActual = this.totalPaginas;
        
          this.cargarProductos();
          return;
        }

        this.loading = false;
      },

      error: () => {
        this.loading = false;
      },
    });
  }

  buscar(): void {
    this.paginaActual = 1;
    this.cargarProductos();
  }

  cambiarPagina(nuevaPagina: number): void {

    if (
      nuevaPagina === this.paginaActual ||
      nuevaPagina < 1 ||
      nuevaPagina > this.totalPaginas
    ) {
      return;
    }
  
    this.paginaActual = nuevaPagina;
  
    this.cargarProductos();
  
  }

  crearProducto(): void {
    this.productoActual = this.nuevoProducto();
    this.imagenSeleccionada = null;
    this.mostrarFormulario = true;
    this.modoEdicion = false;
  }

  editarProducto(producto: ProductoAdmin): void {
    this.productoActual = {
      ...producto,
      categoria_id: producto.categoria?.id,
    };

    this.imagenSeleccionada = null;

    this.mostrarFormulario = true;
    this.modoEdicion = true;
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];

    if (file) {
      this.imagenSeleccionada = file;
    }
  }

  guardarProducto(): void {
    const formData = new FormData();

    formData.append('nombre', this.productoActual.nombre);

    formData.append('descripcion', this.productoActual.descripcion ?? '');

    formData.append('precio', String(this.productoActual.precio));

    formData.append('stock', String(this.productoActual.stock));

    // ✅ categoria_id obligatorio
    if (this.productoActual.categoria_id !== undefined) {
      formData.append('categoria_id', String(this.productoActual.categoria_id));
    }

    // ✅ imagen
    if (this.imagenSeleccionada) {
      formData.append('imagen', this.imagenSeleccionada);
    }

    // 🔥 DEBUG
    console.log('DATOS ENVIADOS:');

    formData.forEach((value, key) => {
      console.log(key, value);
    });

    // =========================
    // EDITAR
    // =========================

    if (this.modoEdicion && this.productoActual.id) {
      this.productosService
        .actualizar(this.productoActual.id, formData)
        .subscribe({
          next: () => {
            this.cargarProductos();
            this.cancelar();
          },

          error: (err) => {
            console.error('ERROR ACTUALIZANDO PRODUCTO');
            console.error(err);

            console.error('RESPUESTA BACKEND:');
            console.error(err.error);
          },
        });
    }

    // =========================
    // CREAR
    // =========================
    else {
      this.productosService.crear(formData).subscribe({
        next: () => {
          this.cargarProductos();
          this.cancelar();
        },

        error: (err) => {
          console.error('ERROR CREANDO PRODUCTO');
          console.error(err);

          console.error('RESPUESTA BACKEND:');
          console.error(err.error);
        },
      });
    }
  }

  cancelar(): void {
    this.mostrarFormulario = false;
    this.productoActual = this.nuevoProducto();
    this.imagenSeleccionada = null;
  }

  confirmarEliminar(id: number): void {
    this.productoAEliminar = id;
  }

  eliminarProducto(): void {
    if (!this.productoAEliminar) return;

    this.productosService.eliminar(this.productoAEliminar).subscribe(() => {
      this.productoAEliminar = null;

      // Si era el único producto de la página,
      // volver una página antes de recargar.
      if (this.productos.length === 1 && this.paginaActual > 1) {
        this.paginaActual--;
      }

      this.cargarProductos();
    });
  }
}
