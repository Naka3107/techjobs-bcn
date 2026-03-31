import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = 'http://localhost:5000';

  // Estado de autenticación reactivo
  token = signal<string | null>(null);
  rol = signal<string | null>(null);
  usuarioId = signal<number | null>(null);

  estaAutenticado = () => this.token() !== null;
  esProgramador = () => this.rol() === 'programador';
  esEmpresa = () => this.rol() === 'empresa';

  login(email: string, contraseña: string) {
    return this.http.post<{token: string, rol: string, usuario_id: number}>(
      `${this.apiUrl}/login`,
      { email, contraseña }
    );
  }

  registrarProgramador(datos: any) {
    return this.http.post(`${this.apiUrl}/registro/programador`, datos);
  }

  registrarEmpresa(datos: any) {
    return this.http.post(`${this.apiUrl}/registro/empresa`, datos);
  }

  guardarSesion(token: string, rol: string, usuario_id: number) {
    this.token.set(token);
    this.rol.set(rol);
    this.usuarioId.set(usuario_id);
  }

  cerrarSesion() {
    this.token.set(null);
    this.rol.set(null);
    this.usuarioId.set(null);
    this.router.navigate(['/']);
  }
}