import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    return parts.pop()!.split(';').shift() || null;
  }

  return null;
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const router = inject(Router);

  const csrfToken = getCookie('csrftoken');

  let modifiedReq = req.clone({
    // ✅ enviar cookies SIEMPRE
    withCredentials: true
  });

  // 🔐 Agregar CSRF si existe
  if (csrfToken) {
    modifiedReq = modifiedReq.clone({
      setHeaders: {
        'X-CSRFToken': csrfToken
      }
    });
  }

  return next(modifiedReq).pipe(

    catchError((error) => {

      // 🔥 CLAVE: manejar sesión inválida
      if (error.status === 401 || error.status === 403) {

        console.warn('Sesión expirada o inválida');

        // limpiar estado frontend
        localStorage.clear();

        // evitar loops infinitos
        if (!router.url.includes('/login')) {
          router.navigate(['/login']);
        }
      }

      return throwError(() => error);
    })

  );
};