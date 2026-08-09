import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminReportingService } from '../../../../services/admin-reporting.service';
import { PaginationComponent } from '../../../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-recomendaciones-report',
  standalone: true,
  imports: [CommonModule, PaginationComponent],
  templateUrl: './recomendaciones-report.component.html'
})
export class RecomendacionesReportComponent implements OnInit {

  reglas: any[] = [];

  loading = true;
  error = '';

  // =========================
  // PAGINACIÓN
  // =========================

  paginaActual = 1;

  totalRegistros = 0;

  totalPaginas = 0;

  pageSize = 15;

  constructor(
    private reportingService: AdminReportingService
  ) {}

  ngOnInit(): void {
    this.cargarReglas();
  }

  cargarReglas(): void {

    this.loading = true;
    this.error = '';

    this.reportingService
      .getReglasAsociacion(this.paginaActual)
      .subscribe({

        next: (data) => {

          this.reglas = data.results;

          this.totalRegistros = data.count;

          this.totalPaginas = Math.ceil(
            this.totalRegistros / this.pageSize
          );

          this.loading = false;

        },

        error: () => {

          this.error = 'Error al cargar recomendaciones';

          this.loading = false;

        }

      });

  }

  cambiarPagina(pagina: number): void {

    if (pagina < 1 || pagina > this.totalPaginas) {
      return;
    }

    this.paginaActual = pagina;

    this.cargarReglas();

  }

}