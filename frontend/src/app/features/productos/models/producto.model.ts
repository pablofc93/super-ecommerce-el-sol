// Modelo real del frontend (dominio)

import { Categoria } from './categoria.model';

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  imagen_url: string;      // nunca null en la UI
  categoria: Categoria | null;
  creado_en: Date;
  actualizado_en: Date;
}