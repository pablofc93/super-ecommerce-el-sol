import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { ProductosService } from '../../services/productos.service';
import { Producto } from '../../models/producto.model';
import { AuthService } from '../../../auth/services/auth.service';
import { Categoria } from '../../models/categoria.model';
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
  vistaCategorias = false;
  categoriasConProductos: { categoria: string; productos: Producto[]; grupos: Producto[][] }[] = [];
  categoriasVisibles = 4;
  incrementoCategorias = 4;

  // ===================================== CARRUSEL CATEGORÍAS =====================================
  indicesActualesCategorias: Map<number, number> = new Map();
  public animacionesCategorias = new Map<number, 'left' | 'right'>();

  // ===================================== MOSTRAR MÁS PRODUCTOS =====================================
  productosVisibles = 12;
  incrementoProductos = 12;

  constructor(private productosService: ProductosService, private authService: AuthService, private router: Router, private route: ActivatedRoute, private categoriaState: CategoriaStateService) {}

  ngOnInit(): void {
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
  get productosVisiblesLista(): Producto[] { return this.productosFiltrados.slice(0, this.productosVisibles); }

  // =============================== NOMBRE DE CATEGORÍA ACTUAL ===============================
  get nombreCategoriaActual(): string {
    if (this.categoriaSeleccionada === null) { return 'Catálogo de Productos'; }
    return this.categorias.find(categoria => categoria.id === this.categoriaSeleccionada)?.nombre ?? this.productosFiltrados[0]?.categoria?.nombre ?? 'Catálogo de Productos';
  }

  // =============================== MOSTRAR MÁS PRODUCTOS ===============================
  mostrarMasProductos(): void { this.productosVisibles = Math.min(this.productosVisibles + this.incrementoProductos, this.productosFiltrados.length); }

  // =============================== CARGA PRODUCTOS ===============================
  private loadProductos(): void {
    this.loading = true; //se activa el estado de carga
    this.error = null; //limpia cualquier error anterior
    this.productosService.getProductos(this.categoriaSeleccionada ?? undefined).subscribe({ //se llama al servicio para obtener los productos

      next: (data) => {
        this.productos = data;  //se devuelven todos los productos obtenidos del backend
        // El backend ya filtra por categoría.
        this.productosFiltrados = data; //se devuelven los productos por categoria, si es que se selecciona alguna
        this.productosVisibles = this.incrementoProductos;
        if (this.vistaCategorias) { this.armarCategorias(data); }
        this.loading = false;
      },
      error: () => { this.error = 'No se pudieron cargar los productos.'; this.loading = false; }
      
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
  get categoriasVisiblesLista() { return this.categoriasConProductos.slice(0, this.categoriasVisibles); }

  mostrarMasCategorias(): void { this.categoriasVisibles = Math.min(this.categoriasVisibles + this.incrementoCategorias, this.categoriasConProductos.length); }

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

  // =============================== ARMAR CATEGORÍAS ===============================
  /** */
  private armarCategorias(productos: Producto[]): void {
    const mapa = new Map<string, Producto[]>();
    
    /*
    recorrre la lista de productos y los agrupa por nombre de categoria
    si un producto no tiene categoria, se agrupa bajo el nombre "Sin categoría"
    */
    productos.forEach((producto) => {
      const nombreCategoria = producto.categoria?.nombre ?? 'Sin categoría';
      if (!mapa.has(nombreCategoria)) { mapa.set(nombreCategoria, []); }
      mapa.get(nombreCategoria)?.push(producto);
    });

    this.categoriasConProductos = [];

    
    mapa.forEach((productosCategoria, categoria) => {
      const primerosOcho = productosCategoria.slice(0, 8);
      const grupos: Producto[][] = [];
      const totalProductos = primerosOcho.length;
      const ventanaVisible = Math.min(4, totalProductos);
      if (totalProductos === 0) { return; }
      for (let i = 0; i < totalProductos; i++) {
        const grupo: Producto[] = [];
        for (let j = 0; j < ventanaVisible; j++) { const indice = (i + j) % totalProductos; grupo.push(primerosOcho[indice]); }
        grupos.push(grupo);
      }
      this.categoriasConProductos.push({ categoria, productos: primerosOcho, grupos });
    });
    this.categoriasConProductos.sort((a, b) => a.categoria.localeCompare(b.categoria));
    this.categoriasVisibles = Math.min(4, this.categoriasConProductos.length);
  }
}