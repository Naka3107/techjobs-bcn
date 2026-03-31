import { Component, input, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { Oferta } from '../models/oferta';

@Component({
  selector: 'app-oferta-card',
  imports: [DecimalPipe],
  templateUrl: './oferta-card.html',
  styleUrl: './oferta-card.scss'
})
export class OfertaCard {
  oferta = input.required<Oferta>();
  modo = input<'lista' | 'tarjeta'>('tarjeta');
  abierta = signal(false);

  toggle() {
    this.abierta.set(!this.abierta());
  }
}