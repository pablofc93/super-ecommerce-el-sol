import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminReportingService } from '../../../../services/admin-reporting.service';

@Component({
  selector: 'app-productos-report',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './productos-report.component.html',
})
export class ProductosReportComponent implements OnInit {
  productos: any[] = [];

  loading = true;
  error = '';

  constructor(private reportingService: AdminReportingService) {}

  ngOnInit(): void {
    this.cargarProductos();
  }

  cargarProductos(): void {
    this.loading = true;
    this.error = '';

    this.reportingService
      .getProductosMasVendidosAgrupados()
      .subscribe({
        next: (data) => {
          this.productos = data;
          this.loading = false;
        },
        error: () => {
          this.error = 'Error al cargar productos';
          this.loading = false;
        },
      });
  }
}
