/**este archivo define la interfaz para un item en el carrito de compras */
export interface CarritoItem {
  id: number;
  producto_nombre: string;
  cantidad: number;
  precio_unitario: number;
  stock: number;
}
