/**
 * Define la estructura de un artículo dentro del carrito.
 */
export interface CarritoItem {
  id: number;
  producto_nombre: string;
  imagen_url: string | null;
  cantidad: number;
  precio_unitario: number;
  stock: number;
}
