import { PedidoEstado } from '../enums/pedido-estado.enum';

export interface PedidoDetalleItem {

  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;

}

export interface PedidoDetalle {

  id_pedido: number;
  cliente_nombre: string;
  total: number;
  estado: PedidoEstado;
  fecha: string;

  items: PedidoDetalleItem[];

}