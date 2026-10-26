import { Component, DestroyRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, finalize, forkJoin, of, switchMap } from 'rxjs';
import { ProductosService } from '../../services/productos.service';
import { Producto } from '../../models/producto.model';
import { AuthService } from '../../../auth/services/auth.service';
import { RecomendacionService } from '../../../recomendacion/services/recomendacion.service';
import { Categoria } from '../../models/categoria.model';
import { CategoriasService } from '../../services/categorias.service';
import { SidebarCategoriasComponent } from '../../../../shared/components/sidebar-categorias/sidebar-categorias.component';
import { ProductGridComponent } from '../../../../shared/components/product-grid/product-grid.component';
import { ProductCardComponent } from '../../../../shared/components/product-card/product-card.component';
import { CategoriaStateService } from '../../../../shared/services/categoria-state.service';

@Component({
  selector: 'app-productos-list',
  standalone: true,
  imports: [CommonModule, RouterModule, SidebarCategoriasComponent, ProductGridComponent, ProductCardComponent],
  templateUrl: './productos-list.component.html',
  styleUrls: ['./productos-list.component.css'],
})
export class ProductosListComponent implements OnInit {
  productos: Producto[] = [];
  productosFiltrados: Producto[] = [];
  categorias: Categoria[] = [];
  categoriaSeleccionada: number | null = null;
  loading = false;
  error: string | null = null;
  recomendaciones: Producto[] = [];
  recomendacionesLoading = false;
  recomendacionesError: string | null = null;
  esCliente = false;
  vistaCategorias = false;
  categoriasConProductos: { categoria: string; productos: Producto[]; grupos: Producto[][] }[] = [];
  categoriasHayMas = false;
  categoriasCargandoMas = false;

  // ===================================== CARRUSEL CATEGORÍAS =====================================
  indicesActualesCategorias: Map<number, number> = new Map();
  public animacionesCategorias = new Map<number, 'left' | 'right'>();

  // ===================================== MOSTRAR MÁS PRODUCTOS =====================================
  productosHayMas = false;
  cargandoMasProductos = false;
  private paginaProductos = 1;
  private paginaCategorias = 1;
  private readonly tamanioPaginaProductos = 12;
  private readonly tamanioPaginaCategorias = 4;

  constructor(
    private productosService: ProductosService,
    private categoriasService: CategoriasService,
    private authService: AuthService,
    private recomendacionService: RecomendacionService,
    private router: Router,
    private route: ActivatedRoute,
    private categoriaState: CategoriaStateService,
    private destroyRef: DestroyRef
  ) {}

  ngOnInit(): void {
    this.authService.user$.pipe(
      takeUntilDestroyed(this.destroyRef),
      switchMap((user) => {
        this.esCliente = user?.tipo_usuario === 'cliente';
        this.recomendaciones = [];
        this.recomendacionesError = null;

        if (!this.esCliente || !user) {
          this.recomendacionesLoading = false;
          return of(null);
        }

        this.recomendacionesLoading = true;
        return this.recomendacionService.obtenerPorCliente(user.id).pipe(
          catchError((error: unknown) => {
            console.error('Error al cargar recomendaciones personalizadas', error);
            this.recomendacionesError = 'No se pudieron cargar tus recomendaciones.';
            return of(null);
          }),
          finalize(() => {
            this.recomendacionesLoading = false;
          })
        );
      })
    ).subscribe((productos) => {
      this.recomendaciones = productos ?? [];
    });

    // =============================== CATEGORÍAS GLOBALES ===============================
    /*el componente se suscribe al estado actual de categorias para poder reutilizarlas*/
    this.categoriaState.categorias$.subscribe((cats) => { this.categorias = cats; });

    // =============================== LEER PARÁMETROS URL ===============================
    /** se lee el parámetro de la URL
     * Si el parámetro view es categorias, se activa la vista de categorías
     * Si el parámetro categoría está presente, se filtran los productos por esa categoría
     * Si no hay parámetros de categorías, se muestran todos los productos
     * Se llama a loadProductos() para cargar los productos
    */
    this.route.queryParams.subscribe((params) => {
      this.vistaCategorias = params['view'] === 'categories';
      if (params['categoria']) { this.categoriaSeleccionada = Number(params['categoria']); } else { this.categoriaSeleccionada = null; }
      this.loadProductos();
    });
  }

  // =============================== PRODUCTOS VISIBLES ===============================
  get productosVisiblesLista(): Producto[] { return this.productosFiltrados; }

  // =============================== NOMBRE DE CATEGORÍA ACTUAL ===============================
  get nombreCategoriaActual(): string {
    if (this.categoriaSeleccionada === null) { return 'Catálogo de Productos'; }
    return this.categorias.find(categoria => categoria.id === this.categoriaSeleccionada)?.nombre ?? this.productosFiltrados[0]?.categoria?.nombre ?? 'Catálogo de Productos';
  }

  // =============================== MOSTRAR MÁS PRODUCTOS ===============================
  mostrarMasProductos(): void {
    if (this.productosHayMas && !this.cargandoMasProductos) {
      this.cargarPaginaProductos(this.paginaProductos + 1, true);
    }
  }

  // =============================== CARGA PRODUCTOS ===============================
  private loadProductos(): void {
    this.error = null;
    this.productos = [];
    this.productosFiltrados = [];
    this.categoriasConProductos = [];
    this.productosHayMas = false;
    this.categoriasHayMas = false;
    this.paginaProductos = 1;
    this.paginaCategorias = 1;

    if (this.vistaCategorias) {
      this.cargarPaginaCategorias(1, false);
      return;
    }

    this.cargarPaginaProductos(1, false);
  }

  private cargarPaginaProductos(pagina: number, agregar: boolean): void {
    if (agregar) {
      this.cargandoMasProductos = true;
    } else {
      this.loading = true;
    }
    this.error = null;

    this.productosService.getProductosPagina(
      pagina,
      this.categoriaSeleccionada ?? undefined,
      this.tamanioPaginaProductos
    ).subscribe({
      next: (respuesta) => {
        this.productos = agregar
          ? [...this.productos, ...respuesta.results]
          : respuesta.results;
        this.productosFiltrados = this.productos;
        this.productosHayMas = respuesta.next !== null;
        this.paginaProductos = pagina;
        this.loading = false;
        this.cargandoMasProductos = false;
      },
      error: (err) => {
        console.error('Error al cargar productos', err);
        this.error = 'No se pudieron cargar los productos.';
        this.loading = false;
        this.cargandoMasProductos = false;
      },
    });
  }

  // =============================== CAMBIO DESDE SIDEBAR ===============================
  /**este método se ejecuta cuando el usuario selecciona una categoría en el sidebar
   * si no se selecciona ninguna categoría, se muestran todos los productos
   * si se selecciona una categoría, se filtran y muestran los productos de esa categoría
   */
  filtrarCategoria(categoriaId: number | null): void {
    this.categoriaSeleccionada = categoriaId;
    if (categoriaId === null) { this.router.navigate(['/productos']); } else { this.router.navigate(['/productos'], { queryParams: { categoria: categoriaId } }); }
  }

  // =============================== VER DETALLE ===============================
  verDetalle(productoId: number): void { this.router.navigate(['/productos', productoId]); }

  // =============================== CATEGORÍAS DESTACADAS ===============================
  get categoriasVisiblesLista() { return this.categoriasConProductos; }

  mostrarMasCategorias(): void {
    if (this.categoriasHayMas && !this.categoriasCargandoMas) {
      this.cargarPaginaCategorias(this.paginaCategorias + 1, true);
    }
  }

  // =============================== CARRUSEL CATEGORÍAS ===============================
  moverCategoriaDerecha(indiceCategoria: number): void {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    const total = this.categoriasConProductos[indiceCategoria].grupos.length;
    this.indicesActualesCategorias.set(indiceCategoria, (indiceActual + 1) % total);
    this.activarAnimacionCategoria(indiceCategoria, 'right');
  }

  moverCategoriaIzquierda(indiceCategoria: number): void {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    const total = this.categoriasConProductos[indiceCategoria].grupos.length;
    this.indicesActualesCategorias.set(indiceCategoria, (indiceActual - 1 + total) % total);
    this.activarAnimacionCategoria(indiceCategoria, 'left');
  }

  private activarAnimacionCategoria(indiceCategoria: number, direccion: 'left' | 'right'): void {
    this.animacionesCategorias.delete(indiceCategoria);
    setTimeout(() => {
      this.animacionesCategorias.set(indiceCategoria, direccion);
      setTimeout(() => { this.animacionesCategorias.delete(indiceCategoria); }, 460);
    });
  }

  obtenerGrupoActualCategoria(indiceCategoria: number): Producto[] {
    const indiceActual = this.indicesActualesCategorias.get(indiceCategoria) || 0;
    return this.categoriasConProductos[indiceCategoria]?.grupos[indiceActual] || [];
  }

  private cargarPaginaCategorias(pagina: number, agregar: boolean): void {
    if (agregar) {
      this.categoriasCargandoMas = true;
    } else {
      this.loading = true;
    }
    this.error = null;

    this.categoriasService.listarPagina(pagina, this.tamanioPaginaCategorias).subscribe({
      next: (respuesta) => {
        const categorias = respuesta.results;
        const productosPorCategoria$ = categorias.map((categoria) =>
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
    categorias: { categoria: string; productos: Producto[]; grupos: Producto[][] }[],
    hayMas: boolean,
    pagina: number,
    agregar: boolean
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
    this.error = 'No se pudieron cargar las categorías.';
    this.loading = false;
    this.categoriasCargandoMas = false;
  }
}