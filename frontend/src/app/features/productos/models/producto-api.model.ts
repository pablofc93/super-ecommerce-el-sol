// Este modelo representa EXACTAMENTE lo que viene del backend (Django)
// No debe reutilizar modelos del frontend

import { CategoriaApi } from './categoria-api.model';

export interface ProductoApi {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string;           // Django → string
  stock: number;
  imagen: string | null;
  imagen_url: string | null;
  categoria: CategoriaApi;  // ❗ modelo API
  creado_en: string;
  actualizado_en: string;
}

