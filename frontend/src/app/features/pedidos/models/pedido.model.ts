export interface Pedido {
  id_pedido: number;
  fecha: string;
  total: number | null;
  estado: string; //pendiente, pagado, cancelado, enviado, entregado
}

/**este modelo representa una respuesta paginada del backend */
export interface PaginatedResponse<T> { //T convierte la estructura en genérica, permitiendo que se pueda usar con cualquier tipo de datos
  count: number; //cantidad total de registros
  next: string | null; //URL de referencia a la siguiente página, si existe
  previous: string | null; //URL de referencia a la página anterior, si existe
  results: T[]; //elementos correspondientes a la página actual
}