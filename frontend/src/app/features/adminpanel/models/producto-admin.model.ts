export interface ProductoAdmin {
  id?: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  stock: number;
  categoria?: any;
  categoria_id?: number;
  imagen?: string;
  imagen_url?: string;
}