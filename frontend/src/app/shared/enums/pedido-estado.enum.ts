export enum PedidoEstado {
  PENDIENTE = 'pendiente',
  PAGADO = 'pagado',
  ENVIADO = 'enviado',
  ENTREGADO = 'entregado',
  CANCELADO = 'cancelado'
}

export const PEDIDO_ESTADOS: PedidoEstado[] = [
  PedidoEstado.PENDIENTE,
  PedidoEstado.PAGADO,
  PedidoEstado.ENVIADO,
  PedidoEstado.ENTREGADO,
  PedidoEstado.CANCELADO
];