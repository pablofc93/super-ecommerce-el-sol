import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';

import { ProductosService } from '../../../productos/services/productos.service';
import { Producto } from '../../../productos/models/producto.model';

import { ProductCardComponent } from '../../../../shared/components/product-card/product-card.component';

import { AuthService } from '../../../auth/services/auth.service';
import { ModalAutenticacionComponent } from '../../../../shared/modal-autenticacion/modal-autenticacion.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ProductCardComponent,
    ModalAutenticacionComponent
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {

  productosMasVendidos: Producto[] = [];

  categoriasConProductos: {
    categoria: string;
    productos: Producto[];
    grupos: Producto[][];
  }[] = [];

  // =====================================
  // CARRUSEL PRODUCTOS MÁS VENDIDOS
  // =====================================

  indiceActualMasVendidos = 0;

  animacionMasVendidos: 'left' | 'right' | null = null;

  // =====================================
  // CARRUSELES DE CATEGORÍAS
  // =====================================

  indicesActualesCategorias: Map<number, number> = new Map();

  animacionesCategorias = new Map<number, 'left' | 'right'>();

  // =====================================
  // MOSTRAR MÁS CATEGORÍAS
  // =====================================

  categoriasVisibles = 4;

  incrementoCategorias = 4;

  // =====================================
  // ESTADO
  // =====================================

  loading = true;

  error: string | null = null;

  // =====================================
  // MODAL AUTENTICACIÓN
  // =====================================

  mostrarModalLogin = false;

  constructor(
    private productosService: ProductosService,
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  // =====================================
  // CARRUSEL PRODUCTOS MÁS VENDIDOS
  // =====================================

  moverMasVendidosDerecha(): void {
    if (this.productosMasVendidos.length === 0) {
      return;
    }

    this.indiceActualMasVendidos =
      (this.indiceActualMasVendidos + 1) %
      this.productosMasVendidos.length;

    this.activarAnimacionMasVendidos('right');
  }

  moverMasVendidosIzquierda(): void {
    if (this.productosMasVendidos.length === 0) {
      return;
    }

    this.indiceActualMasVendidos =
      (this.indiceActualMasVendidos - 1 +
        this.productosMasVendidos.length) %
      this.productosMasVendidos.length;

    this.activarAnimacionMasVendidos('left');
  }

  private activarAnimacionMasVendidos(
    direccion: 'left' | 'right'
  ): void {

    this.animacionMasVendidos = null;

    setTimeout(() => {
      this.animacionMasVendidos = direccion;

      setTimeout(() => {
        this.animacionMasVendidos = null;
      }, 460);
    });
  }

  obtenerProductoActualMasVendido(): Producto | null {
    return (
      this.productosMasVendidos[this.indiceActualMasVendidos] || null
    );
  }

  // =====================================
  // CARRUSEL CATEGORÍAS
  // =====================================

  moverCategoriaDerecha(indiceCategoria: number): void {

    const indiceActual =
      this.indicesActualesCategorias.get(indiceCategoria) || 0;

    const totalDiapositivas =
      this.categoriasConProductos[indiceCategoria].grupos.length;

    this.indicesActualesCategorias.set(
      indiceCategoria,
      (indiceActual + 1) % totalDiapositivas
    );

    this.activarAnimacionCategoria(indiceCategoria, 'right');
  }

  moverCategoriaIzquierda(indiceCategoria: number): void {

    const indiceActual =
      this.indicesActualesCategorias.get(indiceCategoria) || 0;

    const totalDiapositivas =
      this.categoriasConProductos[indiceCategoria].grupos.length;

    this.indicesActualesCategorias.set(
      indiceCategoria,
      (indiceActual - 1 + totalDiapositivas) %
        totalDiapositivas
    );

    this.activarAnimacionCategoria(indiceCategoria, 'left');
  }

  private activarAnimacionCategoria(
    indiceCategoria: number,
    direccion: 'left' | 'right'
  ): void {

    this.animacionesCategorias.delete(indiceCategoria);

    setTimeout(() => {

      this.animacionesCategorias.set(
        indiceCategoria,
        direccion
      );

      setTimeout(() => {
        this.animacionesCategorias.delete(indiceCategoria);
      }, 460);

    });
  }

  obtenerGrupoActualCategoria(
    indiceCategoria: number
  ): Producto[] {

    const indiceActual =
      this.indicesActualesCategorias.get(indiceCategoria) || 0;

    return (
      this.categoriasConProductos[indiceCategoria]
        ?.grupos[indiceActual] || []
    );
  }

  get categoriasVisiblesLista() {
    return this.categoriasConProductos.slice(
      0,
      this.categoriasVisibles
    );
  }

  // =====================================
  // CARGA DE DATOS
  // =====================================

  cargarDatos(): void {

    this.loading = true;

    this.productosService.getProductos().subscribe({

      next: (productos) => {
        this.armarCategorias(productos);
      },

      error: (err) => {

        console.error(err);

        this.error = 'Error al cargar productos';

        this.loading = false;
      },

    });

    this.productosService.getProductosMasVendidos().subscribe({

      next: (productos) => {

        this.productosMasVendidos = productos;

        this.indiceActualMasVendidos = 0;

      },

      error: (err) => {

        console.error(err);

      },

    });
  }

  // =====================================
  // ARMAR CATEGORÍAS
  // =====================================

  private armarCategorias(productos: Producto[]): void {

    const mapa = new Map<string, Producto[]>();

    productos.forEach((producto) => {

      const nombreCategoria =
        producto.categoria?.nombre ?? 'Sin categoría';

      if (!mapa.has(nombreCategoria)) {
        mapa.set(nombreCategoria, []);
      }

      mapa.get(nombreCategoria)?.push(producto);

    });

    this.categoriasConProductos = [];

    mapa.forEach((productosCategoria, categoria) => {

      const primerosOcho =
        productosCategoria.slice(0, 8);

      const totalProductos =
        primerosOcho.length;

      const ventanaVisible = 4;

      const grupos: Producto[][] = [];

      for (
        let i = 0;
        i < totalProductos;
        i++
      ) {

        const grupo: Producto[] = [];

        for (
          let j = 0;
          j < ventanaVisible;
          j++
        ) {

          const indice =
            (i + j) % totalProductos;

          grupo.push(
            primerosOcho[indice]
          );
        }

        grupos.push(grupo);
      }

      this.categoriasConProductos.push({
        categoria,
        productos: primerosOcho,
        grupos,
      });

    });

    this.categoriasConProductos.sort(
      (a, b) =>
        a.categoria.localeCompare(b.categoria)
    );

    this.loading = false;
  }

  // =====================================
  // DETALLE / AUTENTICACIÓN
  // =====================================

  verDetalle(productoId: number): void {

    if (!this.authService.isLoggedIn()) {

      this.mostrarModalLogin = true;

      return;
    }

    this.router.navigate([
      '/productos',
      productoId
    ]);
  }

  cerrarModalLogin(): void {

    this.mostrarModalLogin = false;
  }

  irAlLogin(): void {

    this.mostrarModalLogin = false;

    this.router.navigate([
      '/auth/login'
    ]);
  }

  irAlRegistro(): void {

    this.mostrarModalLogin = false;

    this.router.navigate([
      '/auth/register'
    ]);
  }

  // =====================================
  // MOSTRAR MÁS CATEGORÍAS
  // =====================================

  mostrarMasCategorias(): void {

    this.categoriasVisibles = Math.min(
      this.categoriasVisibles +
        this.incrementoCategorias,
      this.categoriasConProductos.length
    );
  }
}