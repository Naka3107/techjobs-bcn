import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.token();

  // Si hay token, clona la petición añadiendo el header Authorization
  if (token) {
    const reqConToken = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next(reqConToken);
  }

  // Si no hay token, deja pasar la petición sin modificar
  return next(req);
};