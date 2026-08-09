import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

// ✅ CORRECTO
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-grafico-pie',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './grafico-pie.component.html'
})
export class GraficoPieComponent implements OnChanges {

  @Input() labels: string[] = [];
  @Input() data: number[] = [];
  @Input() titulo: string = '';

  pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: [],
    datasets: []
  };

  ngOnChanges() {
    this.pieChartData = {
      labels: this.labels,
      datasets: [
        {
          data: this.data
        }
      ]
    };
  }
}