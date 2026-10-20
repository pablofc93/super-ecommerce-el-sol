
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (
  req,
  next
) => {
  const router = inject(Router);

  // Conserva las opciones de la solicitud y sus encabezados.
  // El token CSRF se obtiene desde el servicio que realiza
  // la operación y se envía explícitamente en X-CSRFToken.
  return next(req).pipe(
    catchError((error) => {
      const detail = error?.error?.detail;

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

        if (!router.url.includes('/login')) {
          router.navigate(['/login']);
        }
      }

      return throwError(() => error);
    })
  );
};
