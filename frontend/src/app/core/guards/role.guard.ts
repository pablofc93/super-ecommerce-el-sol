//Injectable: decorador de Angular que permite indicar 
// que una clase puede ser administrada por el s. de inyección de dependencias
import { Injectable } from '@angular/core'; 

import { CanActivate, ActivatedRouteSnapshot, Router, UrlTree } from '@angular/router';
import { Observable, combineLatest, map, filter, take } from 'rxjs';
import { AuthService } from '../../features/auth/services/auth.service';
import { User } from '../../features/auth/models/user.model';

@Injectable({
  providedIn: 'root'
})
// se define la clase que es posible importarla desde otro lugar de la app
// y debe cumplir con la estructura definida por la interfaz CanActivate
export class RoleGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean | UrlTree> {

    const expectedRole = route.data['role']; //obtiene información asociada a la ruta, en este caso obtiene el rol del usuario, que puede ser: admin

    return combineLatest([ //se combinan 2 observables
      this.authService.user$, //observable del usuario actual
      this.authService.initialized$ //observable que inica si AuthService terminó de inicializarse
    ]).pipe( //pipe permite encadenar valores de RxJS
      filter(([_, initialized]) => initialized === true),
      take(1),
      map(([user]: [User | null, boolean]) => {

        if (!user) {
          return this.router.createUrlTree(['/auth/login']);
        }

        
        if (user.tipo_usuario === expectedRole) {
          return true;
        }

        return this.router.createUrlTree(['/']);
      })
    );
  }
}