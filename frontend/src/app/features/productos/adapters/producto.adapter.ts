/*La responsabilidad de este archivo es transformar el objeto ProductoApi que es la respuesta del backend
en Producto, que es la forma en que trabaja Angular, su estructura*/
import { ProductoApi } from '../models/producto-api.model';
import { Producto } from '../models/producto.model';

export class ProductoAdapter {
  
  /** Recibe un objeto de Django y lo convierte en un nuevo objeto con la estructura utilizada por Angular */
  static fromApi(producto: ProductoApi): Producto {

    return {

      id: producto.id,
      nombre: producto.nombre,
      descripcion: producto.descripcion,
      precio: Number(producto.precio),
      stock: producto.stock,
      imagen_url: producto.imagen_url ?? 'assets/no-image.png', // ?? permite asignar una imagen alternativa cuando el valor de la imagen es null o undefined
      categoria: producto.categoria
        ? {
            id: producto.categoria.id,
            nombre: producto.categoria.nombre
          }
        : {
            id: 0,
            nombre: 'Sin categoría'
          },

      creado_en: new Date(producto.creado_en),
      actualizado_en: new Date(producto.actualizado_en)

    };

  }

  static fromApiList(productos: ProductoApi[]): Producto[] {

    return productos.map(p => this.fromApi(p));

  }

}