import { Component, OnInit, LOCALE_ID } from '@angular/core';
import { CommonModule, registerLocaleData } from '@angular/common';
import localeEsAr from '@angular/common/locales/es-AR';
import { PedidoService } from '../../services/pedido.service';
import { Pedido } from '../../models/pedido.model';

registerLocaleData(localeEsAr);

@Component({
  selector: 'app-mis-pedidos',
  standalone: true,
  imports: [CommonModule],
  providers: [
    {
      provide: LOCALE_ID,
      useValue: 'es-AR'
    }
  ],
  templateUrl: './mis-pedidos.component.html',
  styleUrls: ['./mis-pedidos.component.css']
})
export class MisPedidosComponent implements OnInit {

  pedidos: Pedido[] = [];

  cargando = true;
  error = false;

  // 🔥 PAGINACIÓN
  paginaActual = 1;
  totalRegistros = 0;
  haySiguiente = false;
  hayAnterior = false;

  constructor(private pedidoService: PedidoService) {}

  ngOnInit(): void {
    this.cargarPedidos();
  }

  cargarPedidos(page: number = 1): void {

    this.cargando = true;

    this.pedidoService.listarPedidos(page).subscribe({

      next: (data) => {

        this.pedidos = data.results;

        this.totalRegistros = data.count;
        this.haySiguiente = !!data.next;
        this.hayAnterior = !!data.previous;

        this.paginaActual = page;

        this.cargando = false;
      },

      error: () => {
        this.error = true;
        this.cargando = false;
      }

    });

  }

  siguiente(): void {
    if (this.haySiguiente) {
      this.cargarPedidos(this.paginaActual + 1);
    }
  }

  anterior(): void {
    if (this.hayAnterior) {
      this.cargarPedidos(this.paginaActual - 1);
    }
  }

  cancelarPedido(pedidoId: number): void {

    if (!confirm('¿Seguro que deseas cancelar este pedido?')) {
      return;
    }

    this.pedidoService.cancelarPedido(pedidoId).subscribe({
      next: () => {
        this.cargarPedidos(this.paginaActual);
      }
    });

  }

  badgeEstado(estado: string): string {

    switch (estado) {

      case 'pendiente':
        return 'bg-warning text-dark';

      case 'pagado':
        return 'bg-primary';

      case 'enviado':
        return 'bg-info';

      case 'entregado':
        return 'bg-success';

      case 'cancelado':
        return 'bg-danger';

      default:
        return 'bg-secondary';

    }

  }

}