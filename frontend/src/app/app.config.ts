import { ApplicationConfig, provideZoneChangeDetection, APP_INITIALIZER, LOCALE_ID } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withXsrfConfiguration, withInterceptors, withFetch } from '@angular/common/http';
import { registerLocaleData } from '@angular/common';
import localeEsAr from '@angular/common/locales/es-AR';

import { routes } from './app.routes';
import { AuthService } from './features/auth/services/auth.service';
import { authInterceptor } from './core/interceptors/auth.interceptor';

// 🔥 IMPORTANTE → Chart.js
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';

registerLocaleData(localeEsAr);

/**
 * Inicializa la autenticación al arrancar la app
 * Restaura sesión si existe cookie sessionid
 */
export function initializeAuthFactory(authService: AuthService) {
  return () => authService.initializeAuth();
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),

    provideRouter(routes),

    provideHttpClient(
      withFetch(),
      withXsrfConfiguration({
        cookieName: 'csrftoken',
        headerName: 'X-CSRFToken',
      }),
      withInterceptors([authInterceptor])
    ),

    {
      provide: APP_INITIALIZER,
      useFactory: initializeAuthFactory,
      deps: [AuthService],
      multi: true
    },

    {
      provide: LOCALE_ID,
      useValue: 'es-AR'
    },

    // 🔥🔥🔥 CLAVE → habilita Chart.js en toda la app
    provideCharts(withDefaultRegisterables())
  ]
};