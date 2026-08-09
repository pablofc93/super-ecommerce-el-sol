import { HttpInterceptorFn } from '@angular/common/http';

export const credentialsInterceptor: HttpInterceptorFn = (req, next) => {

  // Solo enviar credenciales a endpoints que lo requieren
  if (
    req.url.includes('/api/auth/') ||
    req.url.includes('/api/pedidos/')
  ) {
    const clonedRequest = req.clone({
      withCredentials: true
    });
    return next(clonedRequest);
  }

  return next(req);
};
