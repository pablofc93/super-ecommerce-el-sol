import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminReportingService } from '../../services/admin-reporting.service';

import { ProductosReportComponent } from './components/productos-report/productos-report.component';
import { ClientesReportComponent } from './components/clientes-report/clientes-report.component';
import { RecomendacionesReportComponent } from './components/recomendaciones-report/recomendaciones-report.component';
import { HistoricosReportComponent } from './components/historicos-report/historicos-report.component';

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [
    CommonModule,
    ProductosReportComponent,
    ClientesReportComponent,
    RecomendacionesReportComponent,
    HistoricosReportComponent
  ],
  templateUrl: './reportes.component.html'
})
export class ReportesComponent implements OnInit {

  tabActivo: 'productos' | 'clientes' | 'recomendaciones' | 'historicos' = 'productos';

  tabs = [
    { key: 'productos', label: 'Productos', icon: '📦' },
    { key: 'clientes', label: 'Clientes', icon: '👥' },
    { key: 'recomendaciones', label: 'Recomendaciones', icon: '🤖' },
    { key: 'historicos', label: 'Históricos', icon: '🕓' }
  ] as const;

  constructor(private reportingService: AdminReportingService) {}

  ngOnInit(): void {
    const tabGuardado = localStorage.getItem('tabReportes');

    if (tabGuardado) {
      this.tabActivo = tabGuardado as any;
    }

    this.registrarVista(this.tabActivo); // 🔥 al entrar
  }

  cambiarTab(tab: 'productos' | 'clientes' | 'recomendaciones' | 'historicos') {
    this.tabActivo = tab;
    localStorage.setItem('tabReportes', tab);

    this.registrarVista(tab); // 🔥 al cambiar
  }

  // 🔥 MAPEO A PANEL REAL
  registrarVista(tab: string) {
    const mapa: any = {
      productos: 'productos',
      clientes: 'usuarios',
      recomendaciones: 'reportes',
      historicos: 'reportes'
    };

    const tipo = mapa[tab];

    if (tipo) {
      this.reportingService.registrarAcceso(tipo).subscribe();
    }
  }
}