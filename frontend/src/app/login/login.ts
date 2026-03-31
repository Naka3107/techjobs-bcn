import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  imports: [RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class Login {
  private authService = inject(AuthService);
  private router = inject(Router);

  email = signal('');
  password = signal('');
  error = signal('');
  cargando = signal(false);

  login() {
    if (!this.email() || !this.password()) {
      this.error.set('Introduce email y contraseña');
      return;
    }

    this.cargando.set(true);
    this.error.set('');

    this.authService.login(this.email(), this.password()).subscribe({
      next: (datos) => {
        this.authService.guardarSesion(datos.token, datos.rol, datos.usuario_id);
        this.cargando.set(false);
        // Redirige según el rol
        if (datos.rol === 'programador') {
          this.router.navigate(['/buscador']);
        } else {
          this.router.navigate(['/ofertas']);
        }
      },
      error: () => {
        this.error.set('Email o contraseña incorrectos');
        this.cargando.set(false);
      }
    });
  }
}