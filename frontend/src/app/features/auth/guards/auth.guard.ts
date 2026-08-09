import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, combineLatest, map, filter, take } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> {

    return combineLatest([
      this.authService.user$,
      this.authService.initialized$
    ]).pipe(
      filter(([_, initialized]) => initialized === true),
      take(1),
      map(([user]) => {
        if (user) {
          return true;
        }

        // 🔥 guardar URL destino
        return this.router.createUrlTree(
          ['/auth/login'],
          { queryParams: { returnUrl: state.url } }
        );
      })
    );
  }
}