
import { HttpInterceptorFn } from '@angular/common/http';

import { environment } from '../../../environments/environment';

export const credentialsInterceptor: HttpInterceptorFn = (
  req,
  next
) => {
  // Envía las cookies al backend cuando la solicitud
  // se dirige a la API configurada.
  if (req.url.startsWith(environment.apiUrl)) {
    return next(
      req.clone({
        withCredentials: true,
      })
    );
  }

  return next(req);
};
