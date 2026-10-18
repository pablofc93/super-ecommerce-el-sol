import {
  Component,
  EventEmitter,
  Input,
  Output,
  OnChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pagination.component.html',
})
export class PaginationComponent implements OnChanges {
  @Input() paginaActual = 1; //paginaActual es una propiedad que recibe información del componente padre

  @Input() totalPaginas = 1;

  @Input() cantidadVisible = 5;

  @Output() paginaChange = new EventEmitter<number>(); //paginaChange es un evento que emite un número (la página seleccionada) al componente padre

  paginas: number[] = [];

  /**método que se ejecuta cuando cambian las propiedades del componente */
  ngOnChanges(): void {
    this.actualizarPaginas();
  }

  /**este método actualiza la lista de páginas visibles
   * si el total de páginas es menor o igual a 0, se vacía la lista de páginas
   */
  private actualizarPaginas(): void {
    if (this.totalPaginas <= 0) {
      this.paginas = [];
      return;
    }

    /**se calcula el rango de páginas visibles */
    let inicio = this.paginaActual - Math.floor(this.cantidadVisible / 2);
    let fin = this.paginaActual + Math.floor(this.cantidadVisible / 2);

    /**el inicio nunca debe ser menor que 1 */
    if (inicio < 1) {
      inicio = 1;
      fin = Math.min(this.cantidadVisible, this.totalPaginas);
    }

    /**el final nunca debe ser mayor que el total de páginas */
    if (fin > this.totalPaginas) {
      fin = this.totalPaginas;
      inicio = Math.max(1, fin - this.cantidadVisible + 1);
    }

    this.paginas = [];

    for (let i = inicio; i <= fin; i++) {
      this.paginas.push(i);
    }
  }

  cambiarPagina(pagina: number): void {
    if (pagina < 1) return;

    if (pagina > this.totalPaginas) return;

    if (pagina === this.paginaActual) return;

    this.paginaChange.emit(pagina);
  }

  mostrarPrimeraPagina(): boolean {
    return this.paginas.length > 0 && this.paginas[0] > 1;
  }

  mostrarPuntosInicio(): boolean {
    return this.paginas.length > 0 && this.paginas[0] > 2;
  }

  mostrarUltimaPagina(): boolean {
    return (
      this.paginas.length > 0 &&
      this.paginas[this.paginas.length - 1] < this.totalPaginas
    );
  }

  mostrarPuntosFin(): boolean {
    return (
      this.paginas.length > 0 &&
      this.paginas[this.paginas.length - 1] < this.totalPaginas - 1
    );
  }
}
