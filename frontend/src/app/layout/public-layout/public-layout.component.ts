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
  selector: 'app-public-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    NavbarComponent,
    SidebarCategoriasComponent,
    FooterComponent
  ],
  templateUrl: './public-layout.component.html',
  styleUrl: './public-layout.component.css'
})
export class PublicLayoutComponent implements OnInit {

  showSidebar = true;

  // Categorías globales para el sidebar
  categorias: Categoria[] = [];

  constructor(
    private router: Router,
    private categoriasService: CategoriasService,
    private categoriaState: CategoriaStateService
  ) {}

  ngOnInit(): void {

    // Ocultar sidebar cuando se navega al panel de administración
    this.router.events
      .pipe(filter(e => e instanceof NavigationEnd))
      .subscribe((e: any) => {
        this.showSidebar = !e.url.startsWith('/admin');
      });

    // Carga inicial de categorías
    this.categoriasService.listar().subscribe({
      next: (cats) => {

        // Guardar en el estado global
        this.categoriaState.setCategorias(cats);

        // Actualizar el sidebar
        this.categorias = cats;
      },
      error: (err) =>
        console.error('Error cargando categorías globales', err)
    });

    // Mantener sincronizado el sidebar si las categorías cambian
    this.categoriaState.categorias$.subscribe(cats => {
      this.categorias = cats;
    });
  }
}