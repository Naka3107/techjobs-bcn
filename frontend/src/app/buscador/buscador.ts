import { Component, inject, signal, ViewChild, ElementRef, OnInit } from '@angular/core';
import { Oferta } from '../models/oferta';
import { Programador } from '../models/programador';
import { OfertaService } from '../services/oferta.service';
import { ProgramadorService } from '../services/programador.service';
import { AuthService } from '../services/auth';
import { OfertaCard } from '../oferta-card/oferta-card';

@Component({
  selector: 'app-buscador',
  imports: [OfertaCard],
  templateUrl: './buscador.html',
  styleUrl: './buscador.scss',
})
export class Buscador implements OnInit {
  private ofertaService = inject(OfertaService);
  private programadorService = inject(ProgramadorService);
  authService = inject(AuthService);

  // Programador
  resultadosOfertas = signal<Oferta[]>([]);
  salarioMinimo = signal<number>(0);
  pais = signal<string>('');

  // Empresa
  resultadosProgramadores = signal<Programador[]>([]);
  experienciaMinima = signal<number>(0);
  ciudad = signal<string>('');
  ofertasEmpresa = signal<Oferta[]>([]);
  ofertaSeleccionada = signal<number | null>(null);
  todasLasOfertas = signal<boolean>(true);

  estado = signal<'idle' | 'ok' | 'error'>('idle');
  vista = signal<'lista' | 'tarjetas'>('lista');

  @ViewChild('carrusel') carruselRef!: ElementRef;

  scrollCarrusel(direccion: number) {
    this.carruselRef.nativeElement.scrollBy({
      left: direccion * 300,
      behavior: 'smooth'
    });
  }

  ngOnInit () {
    if (this.authService.esEmpresa()) {
      this.ofertaService.getOfertasEmpresa().subscribe(data => {
        this.ofertasEmpresa.set(data);
      });
    }
  }

  buscar() {
    if (this.authService.esProgramador()) {
      this.ofertaService.getOfertasCompatibles(this.salarioMinimo() || undefined, this.pais() || undefined)
      .subscribe({
      next: data => {
        this.resultadosOfertas.set(data);
        this.estado.set(data.length === 0 ? 'error' : 'ok');
        if (data.length === 0) alert('No hay ofertas compatibles con estos filtros.');
        },
      error: err => {
        this.estado.set('error');
        if (err.status === 403) alert('Necesitas iniciar sesión como programador para usar el buscador.');
        else alert('Error al buscar ofertas.');
        }
      });
    } else {
      this.programadorService.getProgramadoresCompatibles(
        this.todasLasOfertas() ? undefined : this.ofertaSeleccionada() || undefined,
        this.experienciaMinima() || undefined,
        this.ciudad() || undefined
      ).subscribe({
        next: data => {
          this.resultadosProgramadores.set(data);
          this.estado.set(data.length === 0 ? 'error' : 'ok');
          if (data.length === 0) alert('No hay programadores compatibles con estos filtros.');
        },
        error: () => {
          this.estado.set('error');
          alert('Error al buscar programadores.');
        }
      });
    }
  }
}
