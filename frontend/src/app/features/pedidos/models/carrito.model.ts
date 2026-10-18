import { CarritoItem } from './carrito-item.model';

export interface Carrito {
  id: number;
  cliente: number;
  activo: boolean;
  creado_en: string;
  items: CarritoItem[]; // indica que un carrito puede tener múltiples items (productos) 
}
