/**Este archivo define el componente PublicLayoutComponent, que se encarga de organizar la estructura visual de 
 * las páginas públicas de la aplicación y coordinar la carga y distribución de las categorías de productos en el sidebar.
 * (menú lateral)
 */
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';

import { CategoriasService } from '../../features/productos/services/categorias.service';
import { CategoriaStateService } from '../../shared/services/categoria-state.service';

import { SidebarCategoriasComponent } from '../../shared/components/sidebar-categorias/sidebar-categorias.component';
import { NavbarComponent } from '../../shared/components/navbar/navbar.component';

import { Categoria } from '../../features/productos/models/categoria.model';
import { FooterComponent } from '../../shared/components/footer/footer.component';

@Component({
  selector: 'app-public-layout', // define el nombre mediante el cual se puede utilizar el componente en la plantilla HTML
  standalone: true, // indica que el componente es independiente y no requiere ser declarado en NgModule
  imports: [ // se definen que componentes y módulos se van a utilizar dentro de este componente
    CommonModule,
    RouterModule,
    NavbarComponent,
    SidebarCategoriasComponent,
    FooterComponent
  ],
  templateUrl: './public-layout.component.html', // plantilla HTML que define la estructura visual del componente
  styleUrl: './public-layout.component.css' // hoja de estilos CSS que define la apariencia visual del componente
})
export class PublicLayoutComponent implements OnInit {

  showSidebar = true; //true indica que el sidebar (menú lateral) se muestra por defecto, false indica que está oculto. Se puede cambiar dinámicamente según la ruta actual.

  // Categorías globales para el sidebar
  categorias: Categoria[] = [];
  private categoriasCargando = false;

  /**El constructor recibe las dependencias necesarias para el funcionamiento del componente
   * es decir, se aplica la inyección de dependencias para obtener instancias de los servicios y módulos necesarios
   */
  constructor(
    private router: Router,
    private categoriasService: CategoriasService,
    private categoriaState: CategoriaStateService
  ) {}

  /**este método se ejecuta cuando el componente se inicializa */
  ngOnInit(): void {

    // Ocultar sidebar cuando se navega al panel de administración
    this.router.events
      .pipe(filter(e => e instanceof NavigationEnd))
      .subscribe((e: any) => {
        this.showSidebar = !e.url.startsWith('/admin');
      });

    // Mantener sincronizado el sidebar si las categorías cambian
    this.categoriaState.categorias$.subscribe(cats => {
      this.categorias = cats;
    });
  }

  cargarCategorias(): void {
    if (this.categorias.length > 0 || this.categoriasCargando) {
      return;
    }

    this.categoriasCargando = true;
    this.categoriasService.listar().subscribe({
      next: (categorias) => {
        this.categoriaState.setCategorias(categorias);
        this.categoriasCargando = false;
      },
      error: (err) => {
        console.error('Error cargando categorías globales', err);
        this.categoriasCargando = false;
      },
    });
  }
}