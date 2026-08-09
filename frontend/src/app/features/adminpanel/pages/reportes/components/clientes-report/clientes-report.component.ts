import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminReportingService } from '../../../../services/admin-reporting.service';
import { PaginationComponent } from '../../../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-clientes-report',
  standalone: true,
  imports: [CommonModule, PaginationComponent],
  templateUrl: './clientes-report.component.html',
})
export class ClientesReportComponent implements OnInit {

  clientes: any[] = [];

  loading = true;
  error = '';

  // =========================
  // PAGINACIÓN
  // =========================

  paginaActual = 1;

  totalRegistros = 0;

  totalPaginas = 0;

  // Debe coincidir con el PAGE_SIZE del backend
  pageSize = 15;

  constructor(
    private reportingService: AdminReportingService
  ) {}

  ngOnInit(): void {
    this.cargarClientes();
  }

  cargarClientes(): void {

    this.loading = true;
    this.error = '';

    this.reportingService
      .getIngresosPorCliente(this.paginaActual)
      .subscribe({

        next: (data) => {

          this.clientes = data.results;

          this.totalRegistros = data.count;

          this.totalPaginas = Math.ceil(
            this.totalRegistros / this.pageSize
          );

          this.loading = false;

        },

        error: (err) => {

          console.error(err);

          this.error = 'Error al cargar clientes';

          this.loading = false;

        }

      });

  }

  cambiarPagina(pagina: number): void {

    if (pagina < 1 || pagina > this.totalPaginas) {
      return;
    }

    this.paginaActual = pagina;

    this.cargarClientes();

  }

}