import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminReportingService } from '../../../../services/admin-reporting.service';
import { PaginationComponent } from '../../../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-productos-report',
  standalone: true,
  imports: [CommonModule, FormsModule, PaginationComponent],
  templateUrl: './productos-report.component.html',
})
export class ProductosReportComponent implements OnInit {
  productos: any[] = [];
  historico: any[] = [];

  loading = true;
  error = '';

  filtros = {
    fecha_inicio: '',
    fecha_fin: '',
  };

  // PAGINACIÓN
  paginaActual = 1;
  totalRegistros = 0;
  totalPaginas = 0;

  // ajustar al page_size del backend
  pageSize = 15;

  constructor(private reportingService: AdminReportingService) {}

  ngOnInit(): void {
    this.cargarProductos();
  }

  cargarProductos() {
    this.loading = true;
    this.error = '';

    // 🔥 AGRUPADOS
    this.reportingService
      .getProductosMasVendidosAgrupados(
        this.filtros.fecha_inicio,
        this.filtros.fecha_fin,
      )
      .subscribe({
        next: (data) => {
          this.productos = data;
        },
        error: () => {
          this.error = 'Error al cargar productos';
        },
      });

    // 📜 HISTÓRICO PAGINADO
    this.reportingService.getProductosMasVendidos(this.paginaActual).subscribe({
      next: (resp) => {
        this.historico = resp.results;

        this.totalRegistros = resp.count;

        this.totalPaginas = Math.ceil(this.totalRegistros / this.pageSize);

        this.loading = false;
      },
      error: () => {
        console.warn('Error al cargar histórico');
        this.loading = false;
      },
    });
  }

  aplicarFiltros() {
    this.paginaActual = 1;
    this.cargarProductos();
  }

  limpiarFiltros() {
    this.filtros.fecha_inicio = '';
    this.filtros.fecha_fin = '';
    this.paginaActual = 1;
    this.cargarProductos();
  }

  cambiarPagina(pagina: number): void {
    if (pagina < 1 || pagina > this.totalPaginas) {
      return;
    }

    this.paginaActual = pagina;

    this.cargarProductos();
  }
}
