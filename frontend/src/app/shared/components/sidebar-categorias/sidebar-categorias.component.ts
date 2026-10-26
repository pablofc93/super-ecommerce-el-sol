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

  @Input() categorias: Categoria[] = []; /** Array de categorías. El componente padre envía una lista de categorías */

  @Input() categoriaSeleccionada: number | null = null; // La categoría seleccionada actualmente. El componente padre envía el id de la categoría seleccionada o null si no hay ninguna seleccionada

  @Output()
  categoriaChange = new EventEmitter<number | null>(); // Evento que se emite cuando se selecciona una categoría. Se envía el id de la categoría seleccionada o null si se selecciona "Todos los productos"

  @Output()
  categoriasSolicitadas = new EventEmitter<void>();

  openState = false; // Estado del sidebar. true = abierto, false = cerrado. Se actualiza cuando el usuario pasa el mouse por encima del sidebar o de la zona activadora

  /**
   * El constructor inyecta los servicios necesarios para el funcionamiento del componente:
   * - SidebarService: para controlar el estado del sidebar (abierto/cerrado)
   * - CategoriaStateService: para obtener la lista de categorías globales
   */
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

  /**este método se ejecuta durante la inicialización del componente
   * su objetivo es comprobar si el componente recibió las categorías por input desde el padadre
   * y, si no tiene ninguna, se las obtiene desde el servicio compartido
   */
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
    this.categoriasSolicitadas.emit();
    this.sidebarService.open();
  }

  close(): void {
    this.sidebarService.close();
  }

  seleccionarCategoria(
    id: number | null
  ): void {

    /** Actualiza la categoría seleccionada */
    this.categoriaSeleccionada = id;

    /** Emite el evento de cambio de categoría */
    this.categoriaChange.emit(id);

    /*si el id es null, redirigir a todos los productos
    sino se redirige a la página de productos con el filtro de categoría */
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