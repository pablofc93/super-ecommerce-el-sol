export interface Pedido {
  id_pedido: number;
  fecha: string;
  total: number | null;
  estado: string;
}

// paginación
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}