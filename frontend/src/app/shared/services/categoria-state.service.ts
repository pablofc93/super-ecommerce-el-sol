import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Categoria } from '../../features/productos/models/categoria.model';

@Injectable({
  providedIn: 'root'
})
export class CategoriaStateService {

  private categoriasSubject = new BehaviorSubject<Categoria[]>([]);
  categorias$ = this.categoriasSubject.asObservable();

  setCategorias(categorias: Categoria[]) {
    this.categoriasSubject.next(categorias);
  }

}