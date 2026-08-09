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
  @Input() paginaActual = 1;

  @Input() totalPaginas = 1;

  @Input() cantidadVisible = 5;

  @Output() paginaChange = new EventEmitter<number>();

  paginas: number[] = [];

  ngOnChanges(): void {
    this.actualizarPaginas();
  }

  private actualizarPaginas(): void {
    if (this.totalPaginas <= 0) {
      this.paginas = [];
      return;
    }

    let inicio = this.paginaActual - Math.floor(this.cantidadVisible / 2);

    let fin = this.paginaActual + Math.floor(this.cantidadVisible / 2);

    if (inicio < 1) {
      inicio = 1;
      fin = Math.min(this.cantidadVisible, this.totalPaginas);
    }

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
