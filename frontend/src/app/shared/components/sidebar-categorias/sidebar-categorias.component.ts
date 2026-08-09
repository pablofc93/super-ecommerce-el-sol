import {
  Component,
  EventEmitter,
  Input,
  Output,
  OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { Categoria } from '../../../features/productos/models/categoria.model';

import { SidebarService } from '../../services/sidebar.service';
import { CategoriaStateService } from '../../services/categoria-state.service';

@Component({
  selector: 'app-sidebar-categorias',

  standalone: true,

  imports: [
    CommonModule
  ],

  template: `
    <!-- ZONA ACTIVADORA -->
    <div
      (mouseenter)="open()"
      style="
        position: fixed;
        top: 0;
        left: 0;
        width: 20px;
        height: 100vh;
        z-index: 2000;
      ">
    </div>

    <!-- SIDEBAR -->
    <aside

      (mouseenter)="open()"
      (mouseleave)="close()"

      [style.transform]="openState
        ? 'translateX(0)'
        : 'translateX(-100%)'"

      style="
        position: fixed;
        top: 0;
        left: 0;

        width: 280px;
        height: 100vh;

        background: #212529;
        color: white;

        z-index: 1999;

        overflow-y: auto;

        transition: transform 0.25s ease;

        padding-top: 90px;

        box-shadow: 2px 0 10px rgba(0,0,0,0.3);
      "
    >

      <div class="px-3">

        <h5 class="mb-4 fw-bold">
          Categorías
        </h5>

        <!-- TODOS -->
        <button
          class="btn w-100 text-start mb-2"

          [class.btn-warning]="categoriaSeleccionada === null"

          [class.btn-outline-light]="categoriaSeleccionada !== null"

          (click)="seleccionarCategoria(null)"
        >
          Todos los productos
        </button>

        <!-- CATEGORÍAS -->
        <button
          *ngFor="let categoria of categorias"

          class="btn w-100 text-start mb-2"

          [class.btn-warning]="categoriaSeleccionada === categoria.id"

          [class.btn-outline-light]="categoriaSeleccionada !== categoria.id"

          (click)="seleccionarCategoria(categoria.id)"
        >
          {{ categoria.nombre }}
        </button>

      </div>

    </aside>
  `
})
export class SidebarCategoriasComponent implements OnInit {

  @Input() categorias: Categoria[] = [];

  @Input() categoriaSeleccionada: number | null = null;

  @Output()
  categoriaChange = new EventEmitter<number | null>();

  openState = false;

  constructor(
    private sidebarService: SidebarService,
    private categoriaState: CategoriaStateService,
    private router: Router
  ) {

    this.sidebarService.open$
      .subscribe(value => {
        this.openState = value;
      });

  }

  ngOnInit(): void {

    // Si no llegan por Input, usar las categorías globales
    if (this.categorias.length === 0) {

      this.categoriaState.categorias$
        .subscribe(categorias => {

          this.categorias = categorias;

        });

    }

  }

  open(): void {
    this.sidebarService.open();
  }

  close(): void {
    this.sidebarService.close();
  }

  seleccionarCategoria(
    id: number | null
  ): void {

    this.categoriaSeleccionada = id;

    this.categoriaChange.emit(id);

    // 🔥 REDIRECCIÓN A LISTADO FILTRADO
    if (id === null) {
      this.router.navigate(['/productos']);
    } else {
      this.router.navigate(['/productos'], {
        queryParams: { categoria: id }
      });
    }

    // Cerrar sidebar después de seleccionar
    this.close();

  }

}