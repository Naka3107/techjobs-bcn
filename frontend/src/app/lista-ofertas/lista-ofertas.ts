import { Component, OnInit, inject, signal, ViewChild, ElementRef } from '@angular/core';
import { Oferta } from '../models/oferta';
import { OfertaService } from '../services/oferta.service';
import { AuthService } from '../services/auth';
import { RouterLink } from '@angular/router';
import { OfertaCard } from '../oferta-card/oferta-card';

@Component({
  selector: 'app-lista-ofertas',
  imports: [RouterLink, OfertaCard],
  templateUrl: './lista-ofertas.html',
  styleUrl: './lista-ofertas.scss',
})
export class ListaOfertas implements OnInit {
  ofertas= signal<Oferta[]>([]);
  vista = signal<'lista' | 'tarjetas'>('lista');
  private service = inject(OfertaService);

  authService = inject(AuthService);

  ofertaSeleccionada = signal<number | null>(null);

  @ViewChild('carrusel') carruselRef!: ElementRef;

  scrollCarrusel(direccion: number) {
    const cardWidth = 300; // 280px tarjeta + 20px gap
    this.carruselRef.nativeElement.scrollBy({
      left: direccion * cardWidth,
      behavior: 'smooth'
    });
  }

  toggleOferta(id: number) {
    this.ofertaSeleccionada.set(this.ofertaSeleccionada() === id ? null : id);
  }

  ngOnInit(): void {
  console.log('ngOnInit ejecutado');
  this.service.getOfertas().subscribe(data => {
    console.log('datos recibidos:', data);
    this.ofertas.set(data);
  });
  }
}
