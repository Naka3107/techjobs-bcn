import { Component, inject, signal, ViewChild, ElementRef } from '@angular/core';
import { Oferta } from '../models/oferta';
import { OfertaService } from '../services/oferta.service';
import { OfertaCard } from '../oferta-card/oferta-card';

@Component({
  selector: 'app-buscador',
  imports: [OfertaCard],
  templateUrl: './buscador.html',
  styleUrl: './buscador.scss',
})
export class Buscador {
  resultados = signal<Oferta[]>([]);
  salarioMinimo = signal<number>(0);
  pais = signal<string>('');
  estado = signal<'idle' | 'ok' | 'error'>('idle');

  vista = signal<'lista' | 'tarjetas'>('lista');

  private service = inject(OfertaService);

  @ViewChild('carrusel') carruselRef!: ElementRef;

  scrollCarrusel(direccion: number) {
    this.carruselRef.nativeElement.scrollBy({
      left: direccion * 300,
      behavior: 'smooth'
    });
  }

  buscar() {
    this.service.getOfertasCompatibles(this.salarioMinimo() || undefined, this.pais() || undefined)
      .subscribe({
      next: data => {
        this.resultados.set(data);
        this.estado.set(data.length === 0 ? 'error' : 'ok');
        if (data.length === 0) alert('No hay ofertas compatibles con estos filtros.');
      },
      error: err => {
        this.estado.set('error');
        if (err.status === 403) alert('Necesitas iniciar sesión como programador para usar el buscador.');
        else alert('Error al buscar ofertas. Inténtalo de nuevo más tarde.');
      }
    });
  }
}
