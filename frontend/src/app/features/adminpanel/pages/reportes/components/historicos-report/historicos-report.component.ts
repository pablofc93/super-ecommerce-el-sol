import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminReportingService } from '../../../../services/admin-reporting.service';
import { PaginationComponent } from '../../../../../../shared/components/pagination/pagination.component';

@Component({
  selector: 'app-historicos-report',
  standalone: true,
  imports: [CommonModule, PaginationComponent],
  templateUrl: './historicos-report.component.html'
})
export class HistoricosReportComponent implements OnInit {

  reportes: any[] = [];
  loading = true;
  error = '';

  // 🔥 PAGINACIÓN
  paginaActual = 1;
  totalRegistros = 0;
  totalPaginas = 0;

  // mismo page size que backend (ajustalo si corresponde)
  pageSize = 15;

  tipoLabels: { [key: string]: string } = {
    dashboard: '📊 Dashboard',
    usuarios: '👥 Usuarios',
    productos: '📦 Productos',
    pedidos: '🧾 Pedidos',
    reportes: '📑 Reportes'
  };

  constructor(private reportingService: AdminReportingService) {}

  ngOnInit(): void {
    this.cargarReportes();
  }

  cargarReportes() {
    this.loading = true;
    this.error = '';

    this.reportingService.getReportesHistoricos(this.paginaActual).subscribe({
      next: (resp) => {
        this.reportes = resp.results;
        this.totalRegistros = resp.count;

        this.totalPaginas = Math.ceil(this.totalRegistros / this.pageSize);

        this.loading = false;
      },
      error: () => {
        this.error = 'Error al cargar históricos';
        this.loading = false;
      }
    });
  }

  cambiarPagina(pagina: number): void {
    if (pagina < 1 || pagina > this.totalPaginas) return;

    this.paginaActual = pagina;
    this.cargarReportes();
  }

  getTipoLabel(tipo: string): string {
    return this.tipoLabels[tipo] || tipo;
  }
}