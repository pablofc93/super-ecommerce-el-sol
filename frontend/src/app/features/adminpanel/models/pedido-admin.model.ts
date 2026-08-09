import { PedidoEstado } from '../../../shared/enums/pedido-estado.enum';

export interface PedidoAdmin {

  id_pedido: number;

  cliente_nombre: string;

  total: number;

  estado: PedidoEstado;

  fecha: string;

}