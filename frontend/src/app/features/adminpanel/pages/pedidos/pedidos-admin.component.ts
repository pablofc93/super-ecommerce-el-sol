import {
  Component,
  OnInit,
  OnDestroy,
  inject,
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import {
  EMPTY,
  Subject,
  Subscription,
  of,
  timer,
} from 'rxjs';

import {
  catchError,
  map,
  switchMap,
} from 'rxjs/operators';

import { AdminReportingService } from '../../services/admin-reporting.service';
import { AdminPedidosService } from '../../services/admin-pedidos.service';

import { PedidoAdmin } from '../../models/pedido-admin.model';
import { PedidoDetalle } from '../../../../shared/models/pedido-detalle.model';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';

import {
  PedidoEstado,
  PEDIDO_ESTADOS,
} from '../../../../shared/enums/pedido-estado.enum';

interface SolicitudPedidos {
  page: number;
  search: string;
  debounce: boolean;
}

@Component({
  selector: 'app-pedidos-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    PaginationComponent,
  ],
  templateUrl: './pedidos-admin.component.html',
  styleUrls: ['./pedidos-admin.component.css'],
})
export class PedidosAdminComponent implements OnInit, OnDestroy {

  private pedidosService = inject(AdminPedidosService);
  private reportingService = inject(AdminReportingService);

  private solicitudesPedidos$ = new Subject<SolicitudPedidos>();
  private solicitudesSubscription?: Subscription;

  pedidos: PedidoAdmin[] = [];
  pedidosFiltrados: PedidoAdmin[] = [];

  filtroCliente = '';
  estados = PEDIDO_ESTADOS;

  pedidoDetalle: PedidoDetalle | null = null;
  mostrarModal = false;

  currentPage = 1;
  totalPages = 1;

  ngOnInit(): void {

    this.reportingService.registrarAcceso('pedidos').subscribe({
      error: (err) => {
        console.error('Error registrando acceso al módulo de pedidos', err);
      },
    });

    // Todas las solicitudes de búsqueda y paginación pasan
    // por un mismo flujo para evitar respuestas desactualizadas.
    this.solicitudesSubscription = this.solicitudesPedidos$
      .pipe(
        switchMap((solicitud) => {

          const espera = solicitud.debounce
            ? timer(300)
            : of(0);

          return espera.pipe(
            switchMap(() =>
              this.pedidosService.listarPedidos(
                solicitud.page,
                solicitud.search
              )
            ),

            map((resp) => ({
              resp,
              page: solicitud.page,
            })),

            catchError((err) => {
              console.error('Error cargando pedidos', err);
              return EMPTY;
            })
          );
        })
      )
      .subscribe(({ resp, page }) => {

        this.pedidos = resp.results ?? [];
        this.pedidosFiltrados = [...this.pedidos];

        this.currentPage = page;

        // El backend pagina de a 5 pedidos.
        this.totalPages = Math.max(
          1,
          Math.ceil((resp.count ?? 0) / 5)
        );

      });

    this.cargarPedidos(1);
  }

  /**
   * Solicita pedidos para la página indicada.
   * Utiliza siempre el filtro actual.
   */
  cargarPedidos(page: number = 1): void {

    this.solicitudesPedidos$.next({
      page,
      search: this.filtroCliente.trim(),
      debounce: false,
    });

  }

  /**
   * Cambia de página dentro de los resultados filtrados.
   */
  cambiarPagina(page: number): void {

    if (page < 1 || page > this.totalPages) {
      return;
    }

    this.cargarPedidos(page);
  }

  /**
   * Busca mientras el usuario escribe.
   * Espera 300 ms después de la última tecla.
   * La búsqueda empieza siempre desde la primera página.
   */
  filtrarCliente(): void {

    this.solicitudesPedidos$.next({
      page: 1,
      search: this.filtroCliente.trim(),
      debounce: true,
    });

  }

  cambiarEstado(
    pedido: PedidoAdmin,
    nuevoEstado: PedidoEstado
  ): void {

    const estadoAnterior = pedido.estado;

    pedido.estado = nuevoEstado;

    this.pedidosService
      .cambiarEstado(pedido.id_pedido, nuevoEstado)
      .subscribe({
        error: (err) => {
          pedido.estado = estadoAnterior;

          console.error(
            'Error actualizando el estado del pedido',
            err
          );
        },
      });

  }

  abrirDetalle(pedido: PedidoAdmin): void {

    this.pedidosService
      .detallePedido(pedido.id_pedido)
      .subscribe({
        next: (data) => {
          this.pedidoDetalle = data;
          this.mostrarModal = true;
          document.body.style.overflow = 'hidden';
        },

        error: (err) => {
          console.error('Error cargando detalle', err);
        },
      });

  }

  cerrarModal(): void {

    this.mostrarModal = false;
    this.pedidoDetalle = null;
    document.body.style.overflow = 'auto';

  }

  badgeEstado(estado: PedidoEstado): string {

    switch (estado) {

      case PedidoEstado.PENDIENTE:
        return 'bg-warning';

      case PedidoEstado.PAGADO:
        return 'bg-primary';

      case PedidoEstado.ENVIADO:
        return 'bg-info';

      case PedidoEstado.ENTREGADO:
        return 'bg-success';

      case PedidoEstado.CANCELADO:
        return 'bg-danger';

      default:
        return 'bg-secondary';

    }

  }

  ngOnDestroy(): void {

    this.solicitudesSubscription?.unsubscribe();
    this.solicitudesPedidos$.complete();

    document.body.style.overflow = 'auto';

  }

}
