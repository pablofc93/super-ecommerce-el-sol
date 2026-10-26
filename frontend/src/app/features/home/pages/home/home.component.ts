import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';

import { AuthService } from '../../../auth/services/auth.service';
import { Categoria } from '../../../productos/models/categoria.model';
import { Producto } from '../../../productos/models/producto.model';
import { CategoriasService } from '../../../productos/services/categorias.service';
import { ProductosService } from '../../../productos/services/productos.service';
import { ModalAutenticacionComponent } from '../../../../shared/modal-autenticacion/modal-autenticacion.component';
import { ProductCardComponent } from '../../../../shared/components/product-card/product-card.component';

interface CategoriaConProductos {
  id: number;
  categoria: string;
  productos: Producto[];
  grupos: Producto[][];
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, ProductCardComponent, ModalAutenticacionComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  productosMasVendidos: Producto[] = [];
  categoriasConProductos: CategoriaConProductos[] = [];

  indiceActualMasVendidos = 0;
  animacionMasVendidos: 'left' | 'right' | null = null;
  indicesActualesCategorias: Map<number, number> = new Map();
  animacionesCategorias = new Map<number, 'left' | 'right'>();

  loading = true;
  error: string | null = null;
  categoriasHayMas = false;
  categoriasCargandoMas = false;
  mostrarModalLogin = false;

  private paginaCategorias = 1;
  private readonly tamanioPaginaCategorias = 4;

  constructor(
    private productosService: ProductosService,
    private categoriasService: CategoriasService,
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  moverMasVendidosDerecha(): void {
    if (this.productosMasVendidos.length === 0) return;
    this.indiceActualMasVendidos = (this.indiceActualMasVendidos + 1) % this.productosMasVendidos.length;
    this.activarAnimacionMasVendidos('right');
  }

  moverMasVendidosIzquierda(): void {
    if (this.productosMasVendidos.length === 0) return;
    this.indiceActualMasVendidos = (this.indiceActualMasVendidos - 1 + this.productosMasVendidos.length) % this.productosMasVendidos.length;
    this.activarAnimacionMasVendidos('left');
  }

  private activarAnimacionMasVendidos(direccion: 'left' | 'right'): void {
    this.animacionMasVendidos = null;
    setTimeout(() => {
      this.animacionMasVendidos = direccion;
      setTimeout(() => {
        this.animacionMasVendidos = null;
      }, 460);
    });
  }

  obtenerProductoActualMasVendido(): Producto | null {
    return this.productosMasVendidos[this.indiceActualMasVendidos] || null;
  }

  moverCategoriaDerecha(indiceCategoria: number): void {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    const totalDiapositivas = this.categoriasConProductos[indiceCategoria].grupos.length;
    this.indicesActualesCategorias.set(indiceCategoria, (indiceActual + 1) % totalDiapositivas);
    this.activarAnimacionCategoria(indiceCategoria, 'right');
  }

  moverCategoriaIzquierda(indiceCategoria: number): void {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    const totalDiapositivas = this.categoriasConProductos[indiceCategoria].grupos.length;
    this.indicesActualesCategorias.set(indiceCategoria, (indiceActual - 1 + totalDiapositivas) % totalDiapositivas);
    this.activarAnimacionCategoria(indiceCategoria, 'left');
  }

  private activarAnimacionCategoria(indiceCategoria: number, direccion: 'left' | 'right'): void {
    this.animacionesCategorias.delete(indiceCategoria);
    setTimeout(() => {
      this.animacionesCategorias.set(indiceCategoria, direccion);
      setTimeout(() => {
        this.animacionesCategorias.delete(indiceCategoria);
      }, 460);
    });
  }

  obtenerGrupoActualCategoria(indiceCategoria: number): Producto[] {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    return this.categoriasConProductos[indiceCategoria]?.grupos[indiceActual] || [];
  }

  cargarDatos(): void {
    this.loading = true;
    this.cargarPaginaCategorias(1, false);

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

  private cargarPaginaCategorias(pagina: number, agregar: boolean): void {
    if (agregar) {
      this.categoriasCargandoMas = true;
    } else {
      this.loading = true;
    }

    this.categoriasService.listarPagina(pagina, this.tamanioPaginaCategorias).subscribe({
      next: (respuesta) => {
        const categorias = respuesta.results;
        const productosPorCategoria$ = categorias.map((categoria: Categoria) =>
          this.productosService.getProductosPagina(1, categoria.id, 8)
        );

        if (productosPorCategoria$.length === 0) {
          this.finalizarCargaCategorias([], respuesta.next !== null, pagina, agregar);
          return;
        }

        forkJoin(productosPorCategoria$).subscribe({
          next: (paginasProductos) => {
            const cargadas = categorias.flatMap((categoria, indice) => {
              const productos = paginasProductos[indice].results;
              if (productos.length === 0) return [];

              return [{
                id: categoria.id,
                categoria: categoria.nombre,
                productos,
                grupos: this.crearGruposProductos(productos),
              }];
            });
            this.finalizarCargaCategorias(cargadas, respuesta.next !== null, pagina, agregar);
          },
          error: (err) => this.errorCargaCategorias(err),
        });
      },
      error: (err) => this.errorCargaCategorias(err),
    });
  }

  private crearGruposProductos(productos: Producto[]): Producto[][] {
    const grupos: Producto[][] = [];
    const cantidadVisible = Math.min(4, productos.length);

    for (let indice = 0; indice < productos.length; indice++) {
      const grupo: Producto[] = [];
      for (let desplazamiento = 0; desplazamiento < cantidadVisible; desplazamiento++) {
        grupo.push(productos[(indice + desplazamiento) % productos.length]);
      }
      grupos.push(grupo);
    }

    return grupos;
  }

  private finalizarCargaCategorias(
    categorias: CategoriaConProductos[],
    hayMas: boolean,
    pagina: number,
    agregar: boolean,
  ): void {
    this.categoriasConProductos = agregar
      ? [...this.categoriasConProductos, ...categorias]
      : categorias;
    this.categoriasHayMas = hayMas;
    this.paginaCategorias = pagina;
    this.loading = false;
    this.categoriasCargandoMas = false;
  }

  private errorCargaCategorias(error: unknown): void {
    console.error('Error al cargar categorías y productos', error);
    this.error = 'Error al cargar categorías';
    this.loading = false;
    this.categoriasCargandoMas = false;
  }

  verDetalle(productoId: number): void {
    if (!this.authService.isLoggedIn()) {
      this.mostrarModalLogin = true;
      return;
    }
    this.router.navigate(['/productos', productoId]);
  }

  cerrarModalLogin(): void {
    this.mostrarModalLogin = false;
  }

  irAlLogin(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/login']);
  }

  irAlRegistro(): void {
    this.mostrarModalLogin = false;
    this.router.navigate(['/auth/register']);
  }

  mostrarMasCategorias(): void {
    if (this.categoriasHayMas && !this.categoriasCargandoMas) {
      this.cargarPaginaCategorias(this.paginaCategorias + 1, true);
    }
  }
}
