import { Component, OnInit, inject, signal, ViewChild, ElementRef, computed } from '@angular/core';
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

  paginaActual = signal(0);
  ofertaSeleccionada = signal<number | null>(null);

  ofertasPagina = computed(()=> {
    const inicio = this.paginaActual()*5;
    return this.ofertas().slice(inicio, inicio + 5); 
  });

  totalPaginas = computed(()=> Math.ceil(this.ofertas().length / 5));

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

  paginaSiguiente() {
    if (this.paginaActual() < this.totalPaginas() - 1) {
      this.paginaActual.update(p => p + 1);
    }
  }

  paginaAnterior() {
    if (this.paginaActual() > 0) {
      this.paginaActual.update(p => p - 1);
    }
  }

  eliminarOferta(id: number) {
    if (!confirm('¿Estás seguro que quieres eliminar esta oferta?')) return;
    this.service.eliminarOferta(id).subscribe({
      next: () => {
        this.ofertas.set(this.ofertas().filter(o => o.id !== id));
        if (this.paginaActual() >= this.totalPaginas()) {
          this.paginaActual.update(p => p - 1);
        }
      },
      error: () => alert('Error al eliminar la oferta')
    });
  }

  ngOnInit(): void {
    console.log('ngOnInit ejecutado');
    if (this.authService.rol() === 'empresa') {
      this.service.getOfertasEmpresa().subscribe(data => {
        console.log('datos recibidos para empresa:', data);
        this.ofertas.set(data);
      });
    } else {
      // programador o sin sesión — carga ofertas públicas
      this.service.getOfertas().subscribe(data => {
        console.log('datos recibidos:', data);
        this.ofertas.set(data);
      });
    }
  }
}
