/**
 * HomeComponent se encarga  principalmente de coordinar la información que recibe de los servicios
 * y mostrarla mediante la plantilla HTML de este mismo componente
*/
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; //proporciona funcionalidades como las directivas *ngIf y *ngFor
import { RouterModule, Router } from '@angular/router'; //proporciona funcionalidades relacionadas a las rutas
import { ProductosService } from '../../../productos/services/productos.service';
import { Producto } from '../../../productos/models/producto.model';
import { ProductCardComponent } from '../../../../shared/components/product-card/product-card.component'; //importa el componente reutilizable de las cards de los productos
import { AuthService } from '../../../auth/services/auth.service';
import { ModalAutenticacionComponent } from '../../../../shared/modal-autenticacion/modal-autenticacion.component';
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, ProductCardComponent, ModalAutenticacionComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  
  // ALMACENAR LOS PRODUCTOS MÁS VENDIDOS
  productosMasVendidos: Producto[] = [];

  //ALMACENAR LAS CATEGORÍAS Y LOS PRODUCTOS ASOCIADOS A CADA UNA
  categoriasConProductos: { categoria: string; productos: Producto[]; grupos: Producto[][] }[] = [];

  // CARRUSEL PRODUCTOS MÁS VENDIDOS
  indiceActualMasVendidos = 0;
  animacionMasVendidos: 'left' | 'right' | null = null;

  // CARRUSELES DE CATEGORÍAS
  indicesActualesCategorias: Map<number, number> = new Map();
  animacionesCategorias = new Map<number, 'left' | 'right'>();

  // MOSTRAR MÁS CATEGORÍAS
  categoriasVisibles = 4;
  incrementoCategorias = 4;

  // ESTADO
  loading = true; //indica si todavía se están cargando los datos
  error: string | null = null; //permite almacenar un mensaje cuando ocurre un problema

  // MODAL AUTENTICACIÓN
  mostrarModalLogin = false; //determina si se debe mostrar el modal del login o no, según su estado
  
  constructor( /** el constructor inyecta los servicios */
    private productosService: ProductosService, // para obtener los productos y los productos más vendidos
    private authService: AuthService, // para comprobar si un usuario ya está logueado
    private router: Router, // para navegar por las rutas correspondientes
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  // CARRUSEL PRODUCTOS MÁS VENDIDOS
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

  // CARRUSEL CATEGORÍAS
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

  get categoriasVisiblesLista() {
    return this.categoriasConProductos.slice(0, this.categoriasVisibles);
  }

  // CARGA DE DATOS
  cargarDatos(): void {
    this.loading = true;

    /**
     * se realiza una solicitud al service para traer todos los productos
     * si la solicitud es correcta, se pasan esos productos obtenidos al método
     * armarCategorías para que separe esos productos de acuerdo
     * a su categoría
     */
    this.productosService.getProductos().subscribe({
      next: (productos) => {
        this.armarCategorias(productos);
      },

      /**
       * si ocurre un error en la solicitud de los productor
       * se alamacena ese error
       * y crea un mensaje para mostrar posteriormente ese error
       * al cliente por el frontend
       */
      error: (err) => {
        console.error(err);
        this.error = 'Error al cargar productos';
        this.loading = false;
      },
    });

    /**
     * se realiza una solicitud al service para obtener los productos
     * más vendidos
     */
    this.productosService.getProductosMasVendidos().subscribe({
      next: (productos) => {
        this.productosMasVendidos = productos; //se almacena la respuesta
        this.indiceActualMasVendidos = 0; //se reinicia la posición del carrousel de p. más vendidos
      },
      error: (err) => {
        console.error(err);
      },
    });
  }

  // ARMAR CATEGORÍAS

  /**
   * este método recibe una lista de productos, los agrupa según su categoría y
   * prepara la información necesaria para mostrar los productos en carrouseles de
   * 4 elementos. Finalmente, ordena las categorías alfabéticamente y
   * termina el estado de carga
   */
  private armarCategorias(productos: Producto[]): void {
    
    /**se crea un mapa en donde la clave es la categoría, y el valor es uno o mas elementos del array Producto[]
     * por ejemplo:
     * "Bebidas" → [Producto1, Producto2, Producto3]
     * "Lácteos" → [Producto4, Producto5]
     * "Limpieza" → [Producto6, Producto7, Producto8]
     */
    const mapa = new Map<string, Producto[]>();
    
    /**se recorren todos los productos con un foreach */
    productos.forEach((producto) => {
      /**se obtiene el nombre de la categoria, si no tiene nombre, se le asigna 'sin categoría' */
      const nombreCategoria = producto.categoria?.nombre ?? 'Sin categoría';
      
      /**se comprueba si el mapa ya tiene una clave con ese nombre de categoría
       * si no tiene, se la asigna al mapa, inicialmente con un array vacío
       * queda: 'Bebidas', []
       */
      if (!mapa.has(nombreCategoria)) {
        mapa.set(nombreCategoria, []);
      }
      /**primero se obtiene el array de productos de es cat
       * luego se agrega el producto a ese array
       * ej: 'Bebidas', [agua, Coca-Cola]
       */
      mapa.get(nombreCategoria)?.push(producto);
    });

    this.categoriasConProductos = [];

    mapa.forEach((productosCategoria, categoria) => {
      const primerosOcho = productosCategoria.slice(0, 8); //se toman solo los primeros 8 productos de cada categoría
      const totalProductos = primerosOcho.length; //se define el total de productos a ver en la vista
      const ventanaVisible = 4; //el total de productos visibles en el carrusel
      const grupos: Producto[][] = []; //cada array interno representa un grupo o diapositiva del carrusel

      for (let i = 0; i < totalProductos; i++) {
        const grupo: Producto[] = [];
        for (let j = 0; j < ventanaVisible; j++) {
          const indice = (i + j) % totalProductos;
          grupo.push(primerosOcho[indice]);
        }
        grupos.push(grupo);
      }

      /**cuando se terminan de generar todos los grupos,
       * se agrega un objeto a categoriasProductos
       * ese objeto contiene:
       * nombre de la categoría
       * primeros 8 productos
       * grupos de 4 productos para el carrusel
       */
      this.categoriasConProductos.push({ categoria, productos: primerosOcho, grupos });
    });

    //se ordenan las categorías para que sean mostradas en orden alfabético
    this.categoriasConProductos.sort((a, b) => a.categoria.localeCompare(b.categoria));
    this.loading = false;
  }

  // DETALLE / AUTENTICACIÓN
  verDetalle(productoId: number): void {
    /**si el usuario no está autenticado
     * se muestra el modal de login
     */
    if (!this.authService.isLoggedIn()) {
      this.mostrarModalLogin = true;
      return;
    }
    this.router.navigate(['/productos', productoId]); //ej. redirige a: productos/14
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

  // MOSTRAR MÁS CATEGORÍAS - se aumentan de 4 en 4
  mostrarMasCategorias(): void {
    this.categoriasVisibles = Math.min(this.categoriasVisibles + this.incrementoCategorias, this.categoriasConProductos.length);
  }
}