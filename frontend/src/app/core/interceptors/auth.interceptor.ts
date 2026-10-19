/*
 * Interceptor HTTP de Angular.
 * Envía cookies, agrega CSRF cuando corresponde
 * y gestiona errores de autenticación.
 */

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

  // Enviar cookies de sesión.
  let modifiedReq = req.clone({
    withCredentials: true
  });

  /*
   * Agregar el token disponible solo si la petición
   * todavía no tiene uno explícito.
   *
   * Esto evita sobrescribir el token obtenido desde
   * el endpoint CSRF de Django.
   */
  if (
    csrfToken &&
    !modifiedReq.headers.has('X-CSRFToken')
  ) {
    modifiedReq = modifiedReq.clone({
      setHeaders: {
        'X-CSRFToken': csrfToken
      }
    });
  }

  return next(modifiedReq).pipe(
    catchError((error) => {
      const detail = error?.error?.detail;

      // Un error CSRF no implica necesariamente
      // que la sesión del usuario haya expirado.
      const isCsrfError =
        typeof detail === 'string' &&
        detail.toLowerCase().includes('csrf');

      if (
        (error.status === 401 || error.status === 403) &&
        !isCsrfError
      ) {
        console.warn(
          'Error de autenticación o permisos:',
          error.status
        );

        localStorage.clear();

        if (!router.url.includes('/login')) {
          router.navigate(['/login']);
        }
      }

      return throwError(() => error);
    })
  );
};