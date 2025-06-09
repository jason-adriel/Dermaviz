import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideLoadingBarRouter } from '@ngx-loading-bar/router';
import { provideHttpClient, withFetch, withInterceptors, withInterceptorsFromDi } from '@angular/common/http';
import { provideLoadingBarInterceptor } from '@ngx-loading-bar/http-client';
import { ApiBaseUrlInterceptor } from './_interceptors/api.interceptor';
import { JwtInterceptor } from './_interceptors/jwt.interceptor'

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    providePrimeNG({
        theme: {
            preset: Aura,
            options: {
              prefix: 'p',
              darkModeSelector: '.dark',
            },
        },
    }),
    provideHttpClient(withFetch(), withInterceptors([ApiBaseUrlInterceptor, JwtInterceptor]), withInterceptorsFromDi()),
    provideLoadingBarInterceptor(),
    provideLoadingBarRouter()
  ]
};
