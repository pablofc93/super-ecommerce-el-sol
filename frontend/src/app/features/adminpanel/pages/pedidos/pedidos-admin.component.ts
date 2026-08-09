import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminReportingService } from '../../services/admin-reporting.service'; // 🔥

import { AdminPedidosService } from '../../services/admin-pedidos.service';
import { PedidoAdmin } from '../../models/pedido-admin.model';
import { PedidoDetalle } from '../../../../shared/models/pedido-detalle.model';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';

import {
  PedidoEstado,
  PEDIDO_ESTADOS,
} from '../../../../shared/enums/pedido-estado.enum';

@Component({
  selector: 'app-pedidos-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, PaginationComponent],
  templateUrl: './pedidos-admin.component.html',
  styleUrls: ['./pedidos-admin.component.css'],
})
export class PedidosAdminComponent implements OnInit {
  private pedidosService = inject(AdminPedidosService);
  private reportingService = inject(AdminReportingService); // 🔥

  pedidos: PedidoAdmin[] = [];
  pedidosFiltrados: PedidoAdmin[] = [];

  filtroCliente = '';
  estados = PEDIDO_ESTADOS;

  pedidoDetalle: PedidoDetalle | null = null;
  mostrarModal = false;

  // 🔥 PAGINACIÓN
  currentPage = 1;
  totalPages = 1;

  ngOnInit(): void {
    this.reportingService.registrarAcceso('pedidos').subscribe(); // 🔥
    this.cargarPedidos();
  }

  cargarPedidos(page: number = 1): void {

    this.pedidosService
      .listarPedidos(page, this.filtroCliente)
      .subscribe({
  
        next: (resp) => {
  
          this.pedidos = resp.results;
          this.pedidosFiltrados = resp.results;
  
          this.currentPage = page;
          this.totalPages = Math.ceil(resp.count / 5);
  
        },
  
        error: (err) => console.error('Error cargando pedidos', err),
  
      });
  
  }

  cambiarPagina(page: number): void {
    if (page < 1 || page > this.totalPages) return;

    this.cargarPedidos(page);
  }

  filtrarCliente(): void {

    this.currentPage = 1;
  
    this.cargarPedidos(1);
  
  }

  cambiarEstado(pedido: PedidoAdmin, nuevoEstado: PedidoEstado): void {
    const estadoAnterior = pedido.estado;

    pedido.estado = nuevoEstado;

    this.pedidosService.cambiarEstado(pedido.id_pedido, nuevoEstado).subscribe({
      error: () => {
        pedido.estado = estadoAnterior;
      },
    });
  }

  abrirDetalle(pedido: PedidoAdmin): void {
    this.pedidosService.detallePedido(pedido.id_pedido).subscribe({
      next: (data) => {
        this.pedidoDetalle = data;
        this.mostrarModal = true;
        document.body.style.overflow = 'hidden';
      },
      error: (err) => console.error('Error cargando detalle', err),
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
}
