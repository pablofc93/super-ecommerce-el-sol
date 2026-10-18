import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-grafico-bar',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './grafico-bar.component.html',
  styleUrls: ['./grafico-bar.component.css']
})
/** Este componente se encarga de mostrar un gráfico de barras */
export class GraficoBarComponent implements OnChanges {

  /**Inputs que permiten que el componente reciba datos de su componente padre */
  @Input() labels: string[] = [];
  @Input() data: number[] = [];
  @Input() titulo: string = '';

  @Input() colores: string[] = [];
  @Input() extraInfo: any[] = [];

  @Input() separarDatasets: boolean = false;

  //OPCIONAL (por si se necesita forzar manualmente)
  @Input() mostrarLeyenda: boolean = false;

  /**se crea una propiedad denominada barCharData
   * que almacenará los datos que se mostrarán en el gráfico de barras
   * 'bar' indica que se trata de un gráfico de barras
   * 'data' indica que se trata de los datos del gráfico
   * barCharDara debe tener la estructura de datos correspondiente a un gráfico de barras, 
   * que incluye las etiquetas (labels) y los conjuntos de datos (datasets) que se mostrarán en el gráfico
   */
  barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: []
  };

  /**propiedad que contiene configuración del gráfico */
  barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    plugins: {
      legend: { /**inicialmente la leyenda está oculta */
        display: false
      },
      tooltip: { /** configura las opciones que se muestran cuando el usuario pasa el mouse sobre una barra del gráfico */
        callbacks: {
          label: (context: any) => {
      
            const indice =
              this.separarDatasets
                ? context.datasetIndex
                : context.dataIndex;
      
            const value = context.raw;
      
            const extra = this.extraInfo[indice];
      
            if (!extra) {
              return `${context.dataset.label}: ${value}`;
            }
      
            const gasto = Number(extra.promedio_gasto).toLocaleString(
              'es-AR',
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              }
            );
      
            const pedidos = Number(extra.promedio_pedidos).toLocaleString(
              'es-AR',
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              }
            );
      
            return [
              `${context.dataset.label}: ${value}`,
              `💰 Promedio gasto: $${gasto}`,
              `🛒 Promedio pedidos: ${pedidos}`
            ];
          }
        }
      }
    }
  };

  ngOnChanges() {

    // 🔥 LÓGICA FINAL DE LEYENDA
    const debeMostrarLeyenda =
      this.separarDatasets || this.mostrarLeyenda;

    const currentOptions = this.barChartOptions || {};

    this.barChartOptions = {
      ...currentOptions,
      plugins: {
        ...(currentOptions.plugins || {}),
        legend: {
          display: debeMostrarLeyenda,
          position: 'top'
        }
      }
    };

    const coloresFinal =
      this.colores.length > 0
        ? this.colores
        : this.generarColores(this.data.length);

    // =====================================================
    // CLIENTES (UN DATASET POR CLUSTER)
    // =====================================================
    if (this.separarDatasets) {

      this.barChartData = {
        labels: ['Segmentos'],
        datasets: this.data.map((valor, index) => ({
          label: this.labels[index],
          data: [valor],
          backgroundColor: coloresFinal[index],
        }))
      };

    } else {

      // =====================================================
      // RESTO DE GRÁFICOS
      // =====================================================
      this.barChartData = {
        labels: this.labels,
        datasets: [
          {
            data: this.data,
            label: this.titulo,
            backgroundColor: coloresFinal,
          }
        ]
      };

    }
  }

  generarColores(cantidad: number): string[] {

    const coloresBase = [
      '#FF6384',
      '#36A2EB',
      '#FFCE56',
      '#4BC0C0',
      '#9966FF',
      '#FF9F40',
      '#8BC34A',
      '#E91E63',
      '#00BCD4',
      '#795548'
    ];

    const resultado: string[] = [];

    for (let i = 0; i < cantidad; i++) {
      resultado.push(coloresBase[i % coloresBase.length]);
    }

    return resultado;
  }

}