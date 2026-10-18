/*
Este código es un Interceptor HTTP de Angular
Su función principal es modificar las peticiones que salen desde Angular
hacia Django y, además, reaccionar cuando Django responde con errores 401 o 403
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
//req es una funcion de Angular que se está por enviar, next es una funcion que permite continuar con la peticion
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