import { Component, inject, signal, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { PerfilService } from '../services/perfil.service';
import { AuthService } from '../services/auth';
import { PerfilResponse } from '../models/perfil-response';

@Component({
  selector: 'app-perfil',
  imports: [RouterLink],
  templateUrl: './perfil.html',
  styleUrl: './perfil.scss',
})
export class Perfil implements OnInit {
  private perfilService = inject(PerfilService);
    authService = inject(AuthService);

  perfil = signal<PerfilResponse | null>(null);
  ngOnInit() {
    this.perfilService.getPerfil().subscribe({
      next: (data) => this.perfil.set(data),
      error: (err) => console.error('Error al cargar el perfil', err)
    });
  }
  
  logout() {
    if (confirm('¿Estás seguro que quieres cerrar sesión?')) {
      this.authService.cerrarSesion();
    }
  }
}
