import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router, UrlTree } from '@angular/router';
import { Observable, combineLatest, map, filter, take } from 'rxjs';
import { AuthService } from '../../features/auth/services/auth.service';
import { User } from '../../features/auth/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean | UrlTree> {

    const expectedRole = route.data['role'];

    return combineLatest([
      this.authService.user$,
      this.authService.initialized$
    ]).pipe(
      filter(([_, initialized]) => initialized === true),
      take(1),
      map(([user]: [User | null, boolean]) => {

        if (!user) {
          return this.router.createUrlTree(['/auth/login']);
        }

        // 🔥 CORRECCIÓN AQUÍ
        if (user.tipo_usuario === expectedRole) {
          return true;
        }

        return this.router.createUrlTree(['/']);
      })
    );
  }
}